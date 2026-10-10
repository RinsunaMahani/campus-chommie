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
    # Shown with every result counted this way, e.g. when a rule rests on an assumption.
    note: str | None = None
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


class SourcedText(_Strict):
    """One line of text and the source that says it."""

    text: str = Field(min_length=1)
    source: str


class SourcedList(_Strict):
    """Lines of text from one source, such as the documents an application needs."""

    items: list[str] = Field(min_length=1)
    source: str


class ProgrammeClosing(_Strict):
    """Programmes that close on their own date instead of the window's usual one."""

    closes: date
    programmes: list[str] = Field(min_length=1)
    source: str | None = None  # the window's source when not set


class LateWindow(_Strict):
    """Late applications after the closing date, only when the university publishes them."""

    opens: date
    closes: date
    note: str | None = None
    source: str

    @model_validator(mode="after")
    def _in_order(self):
        if self.closes < self.opens:
            raise ValueError("the late window closes before it opens")
        return self


class Window(_Strict):
    """When people who want to start in `intake` can apply. A date nobody has published stays None."""

    intake: int = Field(ge=2000, le=2100)
    source: str
    opens: date | None = None
    closes: date | None = None  # the usual closing date
    closing_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")  # SAST, e.g. "23:59"
    programme_closes: list[ProgrammeClosing] = Field(default_factory=list)
    # Closing dates a university names without saying which programme closes when.
    closes_one_of: list[date] = Field(default_factory=list)
    late: LateWindow | None = None
    no_late_applications: bool = False  # only when the university says so
    note: str | None = None

    @model_validator(mode="after")
    def _check_dates(self):
        problems: list[str] = []
        closings = [d for d in (self.closes, *self.closes_one_of) if d] + [g.closes for g in self.programme_closes]
        if self.opens and any(d < self.opens for d in closings):
            problems.append(f"{self.intake}: a closing date is before the opening date")
        listed = [p for g in self.programme_closes for p in g.programmes]
        for pid in sorted({p for p in listed if listed.count(p) > 1}):
            problems.append(f"{self.intake}: '{pid}' has more than one closing date")
        if self.late and self.no_late_applications:
            problems.append(f"{self.intake}: late applications are both published and ruled out")
        if self.late and closings and self.late.opens <= max(closings):
            problems.append(f"{self.intake}: late applications open before the last closing date")
        if problems:
            raise ValueError("; ".join(problems))
        self.closes_one_of = sorted(set(self.closes_one_of))
        return self


class Applications(_Strict):
    """How to apply: where, what it costs, what to send, what happens next, and when."""

    source: str | None = None  # cites url, how, fee and contact
    url: str | None = None  # the official page about applying
    how: str | None = None
    fee_cents: int | None = Field(default=None, ge=0)  # None: not verified yet
    fee_note: str | None = None
    contact: str | None = None
    documents: SourcedList | None = None  # None: not verified yet
    after: list[SourcedText] = Field(default_factory=list)
    accepting: SourcedText | None = None  # how to accept an offer; None: not verified yet
    windows: list[Window] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check(self):
        problems: list[str] = []
        own = (self.url, self.how, self.fee_cents, self.fee_note, self.contact)
        if self.source is None and any(v is not None for v in own):
            problems.append("applications: url, how, fee and contact need a source")
        if self.url is not None and not self.url.startswith("https://"):
            problems.append("applications: url must start with https://")
        intakes = [w.intake for w in self.windows]
        if len(set(intakes)) != len(intakes):
            problems.append("applications: one window per intake")
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def citations(self) -> list[tuple[str, str]]:
        """(what, source id) for every fact here, so a pack can check its sources exist."""
        cited = [("applications", self.source)] if self.source else []
        if self.documents:
            cited.append(("applications documents", self.documents.source))
        cited += [("applications after", a.source) for a in self.after]
        if self.accepting:
            cited.append(("applications accepting", self.accepting.source))
        for w in self.windows:
            cited.append((f"window {w.intake}", w.source))
            cited += [(f"window {w.intake}", g.source) for g in w.programme_closes if g.source]
            if w.late:
                cited.append((f"window {w.intake} late", w.late.source))
        return cited


def _unknown_sources(cited: list[tuple[str, str]], source_ids: list[str]) -> list[str]:
    return [f"{what} cites unknown source '{sid}'" for what, sid in cited if sid not in source_ids]


class Campus(_Strict):
    id: str
    name: str
    note: str | None = None  # e.g. which faculties it houses
    source: str


CalendarPeriod = Literal[
    "term", "registration", "orientation", "test_week", "revision", "exam", "recess", "results", "deadline",
    "graduation", "closed",
]


class CalendarEntry(_Strict):
    """A date or period from the university's own calendar. `step` marks the dates a new
    student's first steps come from: registering, orientation and the first lecture."""

    period: CalendarPeriod
    name: str
    start: date
    end: date | None = None  # None: one day
    campuses: list[str] = Field(default_factory=list)  # empty: every campus
    who: Literal["everyone", "first_years", "returning"] = "everyone"
    step: Literal["register", "orientation", "first_lecture"] | None = None
    note: str | None = None
    source: str

    @model_validator(mode="after")
    def _in_order(self):
        if self.end is not None and self.end < self.start:
            raise ValueError(f"'{self.name}' ends before it starts")
        return self

    @property
    def last_day(self) -> date:
        return self.end or self.start


class FundingDate(_Strict):
    """A money date from an official source: fees falling due, a discount ending, a funder paying.
    Dates only, never amounts: amounts in the app are always the student's own entries."""

    funder: Literal["university", "nsfas", "other"]
    kind: Literal["fee_due", "discount_deadline", "allowance", "other"]
    name: str
    when: date  # not "on": YAML reads that key as true
    note: str | None = None
    source: str


SupportKind = Literal[
    "counselling", "crisis", "financial_aid", "food_support", "tutoring", "chaplaincy", "health", "careers",
    "disability",
]


class SupportService(_Strict):
    """Campus support. A crisis line is shown only once a person has verified it (CLAUDE.md)."""

    kind: SupportKind
    name: str
    contact: str  # as the source publishes it: numbers, addresses, rooms
    hours: str | None = None
    campuses: list[str] = Field(default_factory=list)  # empty: every campus
    note: str | None = None
    source: str


class CheapThing(_Strict):
    """Something cheap to do, with its price as its own page states it."""

    name: str
    category: str  # outdoors | heritage | museum | ...
    cost_note: str
    campuses: list[str] = Field(default_factory=list)  # the campuses in its city; empty: every campus
    address: str | None = None  # only when the source page gives it
    hours: str | None = None  # only when the source page gives them
    source: str


class University(_Strict):
    university: str
    name: str
    city: str
    academic_year: int
    release: bool = False
    max_choices: int | None = None
    points_rules: PointsRule | None = None
    applications: Applications | None = None  # None: not verified yet
    campuses: list[Campus] = Field(default_factory=list)
    calendar: list[CalendarEntry] = Field(default_factory=list)
    funding_cycles: list[FundingDate] = Field(default_factory=list)
    support_services: list[SupportService] = Field(default_factory=list)
    cheap_things: list[CheapThing] = Field(default_factory=list)
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
        if self.applications:
            problems += _unknown_sources(self.applications.citations(), source_ids)
            for w in self.applications.windows:
                listed = {pid for g in w.programme_closes for pid in g.programmes}
                for pid in sorted(listed - set(programme_ids)):
                    problems.append(f"window {w.intake}: closing date for unknown programme '{pid}'")
        campus_ids = [c.id for c in self.campuses]
        if len(set(campus_ids)) != len(campus_ids):
            problems.append("campus ids must be unique")
        cited = (
            [(f"campus '{c.id}'", c.source) for c in self.campuses]
            + [(f"calendar '{e.name}'", e.source) for e in self.calendar]
            + [(f"funding date '{f.name}'", f.source) for f in self.funding_cycles]
            + [(f"support '{s.name}'", s.source) for s in self.support_services]
            + [(f"cheap thing '{t.name}'", t.source) for t in self.cheap_things]
        )
        problems += _unknown_sources(cited, source_ids)
        placed = (
            [(f"calendar '{e.name}'", c) for e in self.calendar for c in e.campuses]
            + [(f"support '{s.name}'", c) for s in self.support_services for c in s.campuses]
            + [(f"cheap thing '{t.name}'", c) for t in self.cheap_things for c in t.campuses]
        )
        problems += [f"{what} names unknown campus '{c}'" for what, c in placed if c not in campus_ids]
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


class Funder(_Strict):
    """A national funder learners apply to separately from their university, such as NSFAS."""

    id: str
    name: str
    short_name: str
    who_can_apply: SourcedList | None = None  # shown as the funder words it; we never ask
    tips: SourcedList | None = None  # e.g. the funder's own list of common document mistakes
    warnings: SourcedList | None = None  # e.g. "never pay anyone to apply"
    at_registration: SourcedText | None = None  # what happens to the funding when a student registers
    applications: Applications


class FundingPack(_Strict):
    """National funding (backend/data/national/funding.yaml): the same rules as a university pack."""

    release: bool = False
    funders: list[Funder] = Field(min_length=1)
    sources: list[Source] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_references(self):
        source_ids = [s.id for s in self.sources]
        funder_ids = [f.id for f in self.funders]
        problems: list[str] = []
        if len(set(source_ids)) != len(source_ids):
            problems.append("source ids must be unique")
        if len(set(funder_ids)) != len(funder_ids):
            problems.append("funder ids must be unique")
        for f in self.funders:
            cited = [(f"{f.id}: {what}", sid) for what, sid in f.applications.citations()]
            for what, group in (
                ("who_can_apply", f.who_can_apply), ("tips", f.tips), ("warnings", f.warnings),
                ("at_registration", f.at_registration),
            ):
                if group:
                    cited.append((f"{f.id}: {what}", group.source))
            problems += _unknown_sources(cited, source_ids)
            if any(w.programme_closes or w.closes_one_of for w in f.applications.windows):
                problems.append(f"{f.id}: a funder has one closing date per window, with no programmes to close separately")
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def funder(self, funder_id: str) -> Funder:
        for f in self.funders:
            if f.id == funder_id:
                return f
        raise KeyError(f"no funder '{funder_id}'")

    def source(self, source_id: str) -> Source | None:
        return next((s for s in self.sources if s.id == source_id), None)
