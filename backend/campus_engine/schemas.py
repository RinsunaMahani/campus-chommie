"""Data-pack schemas.

A data pack is one YAML file per university. Every fact-bearing record cites a
source id, and validation fails if a citation or a programme reference is broken.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Guarantee = Literal["by_rule", "considered"]


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
    scale: list[ScaleBand]

    @model_validator(mode="after")
    def _scale_starts_at_zero(self):
        if not any(band.min_percent == 0 for band in self.scale):
            raise ValueError("points scale must include a band starting at 0%")
        return self


class Requirements(_Strict):
    source: str
    min_points: float
    subject_minimums: dict[str, int] = Field(default_factory=dict)
    # Minimum levels for the learner's best remaining subjects, in order.
    additional_minimums: list[int] = Field(default_factory=list)
    # Only set when the university publishes a competitive cut-off.
    competitive_points: float | None = None
    extras: list[str] = Field(default_factory=list)


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
