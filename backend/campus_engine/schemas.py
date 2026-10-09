"""Data-pack schemas.

A data pack is one YAML file per university. Every fact-bearing record cites a
source id, and validation fails if a citation or a programme reference is broken.
"""
from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Guarantee = Literal["by_rule", "considered"]
Level = Annotated[int, Field(ge=1, le=8)]
Percent = Annotated[int, Field(ge=0, le=100)]

# Subject keys a data pack may use in its requirements. Learners' marks use the same keys,
# so a misspelt key would quietly fail every learner; validation rejects unknown ones.
SUBJECTS = frozenset(
    {
        "english",  # English Home Language or English First Additional Language
        "other_language",  # the learner's other official language, at home or first additional level
        "life_orientation",
        "mathematics",
        "technical_mathematics",
        "mathematical_literacy",
        "physical_sciences",
        "technical_sciences",
        "life_sciences",
        "accounting",
        "business_studies",
        "economics",
        "geography",
        "history",
        "agricultural_sciences",
        "agricultural_technology",
        "information_technology",
        "computer_applications_technology",
        "engineering_graphics_and_design",
        "civil_technology",
        "electrical_technology",
        "mechanical_technology",
        "consumer_studies",
        "hospitality_studies",
        "tourism",
        "dance_studies",
        "design",
        "dramatic_arts",
        "music",
        "visual_arts",
    }
)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(_Strict):
    id: str
    url: str
    publisher: str
    title: str | None = None
    retrieved: date | None = None
    last_verified: date | None = None
    verified_by: str | None = None


class ScaleBand(_Strict):
    min_percent: int = Field(ge=0, le=100)
    level: int = Field(ge=1, le=8)


class PointsRule(_Strict):
    """How one university turns school marks into points."""

    source: str
    subjects_counted: int = Field(default=7, ge=1, le=9)
    life_orientation: Literal["full", "half", "exclude"] = "full"
    # Subjects below this level add no points (TUT: 2, because a level 1 isn't counted).
    count_from_level: int = Field(default=1, ge=1, le=8)
    scale: list[ScaleBand]

    @model_validator(mode="after")
    def _scale_starts_at_zero(self):
        if not any(band.min_percent == 0 for band in self.scale):
            raise ValueError("points scale must include a band starting at 0%")
        return self


class Option(_Strict):
    """One way to meet an either/or requirement: every subject listed, at its level."""

    subjects: dict[str, Level] = Field(min_length=1)
    # Set when the university asks a different minimum of learners on this route,
    # for example 28 points with Mathematical Literacy against 26 with Mathematics.
    min_points: float | None = Field(default=None, ge=0)


class Choice(_Strict):
    """An either/or requirement: the learner needs one of the options."""

    one_of: list[Option] = Field(min_length=2)


class Requirements(_Strict):
    source: str
    min_points: float = Field(ge=0)
    subject_minimums: dict[str, Level] = Field(default_factory=dict)
    # Minimum percentages, for universities that set them instead of levels.
    subject_min_percents: dict[str, Percent] = Field(default_factory=dict)
    # Either/or requirements: the learner meets one option in every choice. When the chosen
    # options set their own min_points, the highest of them replaces min_points.
    choices: list[Choice] = Field(default_factory=list)
    # Minimum levels for the learner's best remaining subjects, in order.
    additional_minimums: list[Level] = Field(default_factory=list)
    # Only set when the university publishes a competitive cut-off.
    competitive_points: float | None = None
    extras: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_subjects(self):
        problems: list[str] = []
        rules: list[tuple[str, set[str]]] = [
            ("a minimum level", set(self.subject_minimums)),
            ("a minimum percentage", set(self.subject_min_percents)),
        ] + [
            (f"choice {i + 1}", {s for option in choice.one_of for s in option.subjects})
            for i, choice in enumerate(self.choices)
        ]
        named = [s for _, subjects in rules for s in subjects]
        for subject in sorted(set(named) - SUBJECTS):
            problems.append(f"unknown subject '{subject}'")
        for subject in sorted({s for s in named if named.count(s) > 1}):
            places = [where for where, subjects in rules if subject in subjects]
            problems.append(f"'{subject}' appears in more than one rule ({', '.join(places)})")
        if self.competitive_points is not None and self.competitive_points < self.min_points:
            problems.append("competitive_points is below min_points")
        if problems:
            raise ValueError("; ".join(problems))
        return self


class Bridge(_Strict):
    """A published route from one programme into another."""

    to: str
    guarantee: Guarantee
    conditions: str
    source: str
    max_places: int | None = None
    added_years: int | None = None
    eligibility_note: str | None = None


class Programme(_Strict):
    id: str
    name: str
    fields: list[str] = Field(default_factory=list)
    selective: bool = False
    places: int | None = None
    selection_note: str | None = None
    requirements: Requirements | None = None  # None means not verified yet
    # Only set when this programme counts points differently from the rest of the university.
    points_rules: PointsRule | None = None
    bridges_to: list[Bridge] = Field(default_factory=list)


class University(_Strict):
    university: str
    name: str
    city: str
    academic_year: int
    release: bool = False
    max_choices: int | None = None
    points_rules: PointsRule | None = None
    programmes: list[Programme] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_references(self):
        source_ids = [s.id for s in self.sources]
        programme_ids = [p.id for p in self.programmes]
        problems: list[str] = []
        if len(set(source_ids)) != len(source_ids):
            problems.append("source ids must be unique")
        if len(set(programme_ids)) != len(programme_ids):
            problems.append("programme ids must be unique")
        if self.points_rules and self.points_rules.source not in source_ids:
            problems.append(f"points_rules cites unknown source '{self.points_rules.source}'")
        for p in self.programmes:
            if p.requirements and p.requirements.source not in source_ids:
                problems.append(f"{p.id}: requirements cite unknown source '{p.requirements.source}'")
            if p.points_rules and p.points_rules.source not in source_ids:
                problems.append(f"{p.id}: points_rules cite unknown source '{p.points_rules.source}'")
            for b in p.bridges_to:
                if b.to == p.id:
                    problems.append(f"{p.id}: bridge points to itself")
                elif b.to not in programme_ids:
                    problems.append(f"{p.id}: bridge points to unknown programme '{b.to}'")
                if b.source not in source_ids:
                    problems.append(f"{p.id}: bridge cites unknown source '{b.source}'")
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def programme(self, programme_id: str) -> Programme:
        for p in self.programmes:
            if p.id == programme_id:
                return p
        raise KeyError(f"{self.university} has no programme '{programme_id}'")

    def source(self, source_id: str) -> Source | None:
        return next((s for s in self.sources if s.id == source_id), None)
