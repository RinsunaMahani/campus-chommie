"""Data-pack schemas.

A data pack is one YAML file per university. Every fact-bearing record cites a
source id, and validation fails if a citation or a programme reference is broken.
"""
from __future__ import annotations

from datetime import date
import re
from urllib.parse import urlsplit
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

# Field tags, with the words the app shows. A programme's tags link it to related programmes and to the
# funders of its fields, so a misspelt tag would quietly link nothing; validation rejects unknown ones.
FIELDS: dict[str, str] = {
    "accounting": "Accounting",
    "agriculture": "Agriculture",
    "arts_and_design": "Arts and design",
    "built_environment": "Built environment",
    "commerce": "Commerce",
    "computing": "Computing and IT",
    "consumer_sciences": "Consumer sciences",
    "dentistry": "Dentistry and oral health",
    "disaster_and_fire": "Disaster management and fire",
    "earth_sciences": "Earth and environmental sciences",
    "economics": "Economics",
    "education": "Education and teaching",
    "emergency_care": "Emergency medical care",
    "engineering": "Engineering",
    "environmental_health": "Environmental health",
    "finance": "Finance",
    "food_science": "Food science",
    "health_sciences": "Health sciences",
    "humanities": "Humanities",
    "languages_and_communication": "Languages and communication",
    "law": "Law",
    "life_sciences": "Life sciences",
    "management": "Management",
    "mathematical_sciences": "Mathematics and statistics",
    "medical_sciences": "Medical sciences",
    "medicine": "Medicine",
    "music": "Music",
    "natural_sciences": "Natural sciences",
    "nursing": "Nursing",
    "nutrition": "Nutrition and dietetics",
    "performing_arts": "Performing arts",
    "pharmacy": "Pharmacy",
    "physical_sciences": "Physical sciences",
    "public_administration": "Public administration",
    "radiography": "Radiography",
    "rehabilitation": "Rehabilitation and therapy",
    "safety_and_justice": "Safety and justice",
    "sport_science": "Sport science",
    "theology": "Theology",
    "tourism_and_hospitality": "Tourism and hospitality",
    "veterinary": "Veterinary science",
}


def _unknown_fields(tags: list[str]) -> list[str]:
    return [f"unknown field '{tag}'" for tag in tags if tag not in FIELDS]


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
    verification_basis: Literal["official_university", "official_publisher"] | None = None

    @model_validator(mode="after")
    def _official_origin(self):
        if self.verification_basis is not None:
            parsed = urlsplit(self.url)
            host = (parsed.hostname or "").lower()
            domains = ("cput.ac.za", "cut.ac.za", "dut.ac.za", "mut.ac.za", "mandela.ac.za",
                       "nwu.ac.za", "ru.ac.za", "smu.ac.za", "spu.ac.za", "sun.ac.za", "tut.ac.za",
                       "uct.ac.za", "ufh.ac.za", "ufs.ac.za", "uj.ac.za", "ukzn.ac.za", "ul.ac.za",
                       "ump.ac.za", "unisa.ac.za", "univen.ac.za", "unizulu.ac.za", "up.ac.za",
                       "uwc.ac.za", "vut.ac.za", "wits.ac.za", "wsu.ac.za", "su.ac.za")
            if self.verification_basis == "official_publisher":
                domains += ("gov.za", "nsfas.org.za", "isfap.org.za", "saica.org.za",
                            "thuthukabursaryfund.co.za", "resbank.co.za", "allangrayorbis.org",
                            "clicksgroup.co.za", "csir.co.za", "harmony.co.za", "nedbank.co.za",
                            "ey.com", "hwseta.org.za", "feenix.org", "sasolbursaries.com",
                            "oldmutual.co.za", "cao.ac.za", "ditsong.org.za", "vtm.org.za",
                            "freedompark.co.za", "sanbi.org", "nationalmuseum.co.za",
                            "artmuseum.co.za", "sanlamartcollection.co.za", "whag.co.za", "iziko.org.za",
                            "amazwi.museum", "nelsonmandelamuseum.org.za", "gauteng.net", "elmuseum.za.org")
            if (parsed.scheme != "https" or parsed.username or parsed.password or not self.retrieved
                    or not any(host == d or host.endswith("." + d) for d in domains)):
                raise ValueError("Official verification needs a dated HTTPS source on an approved publisher domain")
        return self

    @property
    def verified(self) -> bool:
        """Dated official provenance is sufficient under Rinsuna's 25 October decision."""
        return self.human_verified or self.verification_basis is not None

    @property
    def evidence_date(self) -> date | None:
        return self.last_verified if self.human_verified else self.retrieved if self.verified else None

    @property
    def human_verified(self) -> bool:
        """A dated, named human review; retrieval or an agent's review is not sign-off."""
        reviewer = (self.verified_by or "").strip().casefold()
        automated = re.match(r"(?:agent|ai|codex|claude|chatgpt|gpt|automated)(?:\b|_)", reviewer)
        return bool(self.last_verified and reviewer and not automated)


class ScaleBand(_Strict):
    min_percent: int = Field(ge=0, le=100)
    level: int = Field(ge=1, le=8)


class PointsBand(_Strict):
    """From this percentage up, a subject adds these points (a university's own table)."""

    min_percent: int = Field(ge=0, le=100)
    points: float = Field(ge=0, le=20)


class PercentPoints(_Strict):
    """Points straight from the percentage: UNIVEN scores 75% as 7.5 and nothing under 40%."""

    per_percent: float = Field(gt=0, le=1)
    from_percent: int = Field(default=0, ge=0, le=100)


class PointsHow(_Strict):
    """How to work out your points where we can't add them up for you: the university's own words and source, its
    own calculator where it has one, and, where it selects on an average, how many best subjects that average takes."""

    text: str = Field(min_length=1)
    source: str
    link: str | None = None
    # Stellenbosch: "the six best Matric subjects' percentages (excluding Life Orientation)".
    average_of_best: int | None = Field(default=None, ge=1, le=9)


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
    # A subject's own points, where the university gives it a table of its own (Wits adds 2 for English
    # and Mathematics from 60%; its Life Orientation table tops out at 4). Others add their level.
    subject_points: dict[str, list[PointsBand]] = Field(default_factory=dict)
    # Every other subject's points, where the university gives them a table too (UWC: 8 at 90%, nothing under 20%).
    other_points: list[PointsBand] = Field(default_factory=list)
    # Set when a subject's points come straight from its percentage instead of its level.
    percent_points: PercentPoints | None = None

    @model_validator(mode="after")
    def _scale_starts_at_zero(self):
        if not any(band.min_percent == 0 for band in self.scale):
            raise ValueError("points scale must include a band starting at 0%")
        tables = dict(self.subject_points)
        if self.other_points:
            tables["other subjects"] = self.other_points
        for subject, table in tables.items():
            if subject not in SUBJECTS and subject != "other subjects":
                raise ValueError(f"subject_points names unknown subject '{subject}'")
            if not any(band.min_percent == 0 for band in table):
                raise ValueError(f"{subject}'s points table must include a band starting at 0%")
            if len({band.min_percent for band in table}) != len(table):
                raise ValueError(f"{subject}'s points table repeats a percentage")
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
    english_language_levels: dict[Literal["home", "first_additional"], Level] = Field(default_factory=dict)
    # Some subject routes have a published APS while another route's threshold is omitted.
    points_threshold_incomplete: bool = False
    # Above a published bounded range, refer to the university instead of extrapolating eligibility.
    max_assessed_points: float | None = Field(default=None, ge=0)
    # Published routes involving prior qualifications/experience cannot be checked from school marks.
    alternative_entry: str | None = None
    alternative_entry_subjects: list[str] = Field(default_factory=list)
    # null when the university publishes no points minimum for this programme: only the subjects are checked.
    # The key is still required, so a pack says so on purpose.
    min_points: float | None = Field(ge=0)
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
        if self.max_assessed_points is not None:
            minima = [self.min_points] + [o.min_points for c in self.choices for o in c.one_of]
            if any(m is not None and m > self.max_assessed_points for m in minima):
                problems.append("assessed points maximum must not be below a route minimum")
        if self.alternative_entry_subjects and not self.alternative_entry:
            problems.append("alternative entry subjects need a published alternative entry note")
        if set(self.alternative_entry_subjects) - (set(self.subject_minimums) | set(self.subject_min_percents)):
            problems.append("alternative entry subjects must name a required subject")
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
        if self.competitive_points is not None and self.min_points is not None and self.competitive_points < self.min_points:
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
    # The university's own name for the faculty, school or college that offers it, from the pack's source.
    # None where the source doesn't say: the app groups those under "Other programmes".
    faculty: str | None = Field(default=None, min_length=1)
    requirements: Requirements | None = None  # None means not verified yet
    # Only set when this programme counts points differently from the rest of the university.
    points_rules: PointsRule | None = None
    bridges_to: list[Bridge] = Field(default_factory=list)

    @model_validator(mode="after")
    def _known_fields(self):
        problems = _unknown_fields(self.fields)
        if problems:
            raise ValueError(f"{self.id}: " + "; ".join(problems))
        return self


class SourcedText(_Strict):
    """One line of text and the source that says it."""

    text: str = Field(min_length=1)
    source: str


class SourcedList(_Strict):
    """Lines of text from one source, such as the documents an application needs."""

    items: list[str] = Field(min_length=1)
    source: str


class HouseholdIncome(_Strict):
    """What a funder's own page says about household income, in its words. Shown, never asked: the app never asks a
    learner about income. `limit_cents` is the highest household income the funder names (None when it names none);
    `missing_middle` is True only when the funder's own words say it serves students above NSFAS's limit (the
    "missing middle", or any household income)."""

    says: str = Field(min_length=1)
    source: str
    limit_cents: int | None = Field(default=None, ge=0)
    missing_middle: bool = False


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


class Seen(_Strict):
    """What a page said when we read it, for a page that says applications are open, or closed,
    without giving the dates. Cited by its window's source."""

    status: Literal["open", "closed"]
    checked: date  # the day we read it


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
    seen: Seen | None = None  # only when the page gives no opening date
    note: str | None = None

    @model_validator(mode="after")
    def _check_dates(self):
        problems: list[str] = []
        closings = [d for d in (self.closes, *self.closes_one_of) if d] + [g.closes for g in self.programme_closes]
        if self.opens and any(d < self.opens for d in closings):
            problems.append(f"{self.intake}: a closing date is before the opening date")
        if self.seen and self.opens:
            problems.append(f"{self.intake}: 'seen' is only for a page that gives no opening date")
        if self.seen and self.seen.status == "open" and any(d < self.seen.checked for d in closings):
            problems.append(f"{self.intake}: seen open after its closing date")
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
    """Campus support. Crisis lines require accepted verification evidence (CLAUDE.md)."""

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


Province = Literal[
    "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "North West",
    "Northern Cape", "Western Cape",
]
#: As a university's own page states its type (DHET groups public universities into general academic,
#: comprehensive and universities of technology). Only set where the university's page says it.
InstitutionType = Literal["university_of_technology", "comprehensive"]


class University(_Strict):
    university: str
    name: str
    city: str
    academic_year: int
    release: bool = False
    # Where its main campus is, and its type, each only as a cited page states it; None until then.
    province: Province | None = None
    province_source: str | None = None
    institution_type: InstitutionType | None = None
    institution_type_source: str | None = None
    max_choices: int | None = None
    points_rules: PointsRule | None = None
    # Why there's no points rule, when there isn't one: shown to the learner instead of a number.
    points_note: str | None = None
    # How a learner works out their points (or average) here themselves, when we can't: quoted from the university.
    points_how: PointsHow | None = None
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
        if self.points_how and self.points_how.source not in source_ids:
            problems.append(f"points_how cites unknown source '{self.points_how.source}'")
        for value, source, what in ((self.province, self.province_source, "province"),
                                    (self.institution_type, self.institution_type_source, "institution_type")):
            if value is not None and (source is None or source not in source_ids):
                problems.append(f"{what} needs a source from this pack's sources")
            if value is None and source is not None:
                problems.append(f"{what}_source given without a {what}")
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


FunderKind = Literal["bursary", "merit_award", "loan"]  # a merit award is paid without an application
Sector = Literal["government", "university", "company", "non_profit"]
Stage = Literal["first_year", "senior", "postgraduate"]  # starting university, already studying, postgraduate
Applying = Literal["direct", "automatic", "via_university"]


class Funder(_Strict):
    """A funder learners apply to separately from their university, such as NSFAS or a bursary.

    The tags say what the funder's own pages say, so the app can sort and match: the fields it funds,
    who it's for and where it can be used. Eligibility in the funder's words (`who_can_apply`) is
    shown, never asked: the learner decides."""

    id: str = Field(pattern=r"^[a-z0-9_]{1,40}$")  # in the API's paths, and kept with a student's saved funding
    name: str
    short_name: str
    kind: FunderKind = "bursary"
    sector: Sector
    every_plan: bool = False  # shown with every course-finder plan, whatever its fields (NSFAS)
    fields: Literal["any"] | list[str]  # field tags it funds, or "any"
    not_fields: list[str] = Field(default_factory=list)  # tags it rules out, e.g. medicine
    stages: list[Stage] = Field(min_length=1)
    study_at: Literal["any"] | list[str] = "any"  # our university ids when it names some; [] when none of ours
    applying: Applying = "direct"
    who_can_apply: SourcedList | None = None  # shown as the funder words it; we never ask
    covers: SourcedList | None = None  # what it pays for, as the funder lists it
    obligations: SourcedList | None = None  # e.g. working for the funder a year for every year funded
    tips: SourcedList | None = None  # e.g. the funder's own list of common document mistakes
    warnings: SourcedList | None = None  # e.g. "never pay anyone to apply"
    at_registration: SourcedText | None = None  # what happens to the funding when a student registers
    income: HouseholdIncome | None = None  # the funder's own words on household income, where it says something
    applications: Applications

    @model_validator(mode="after")
    def _check_tags(self):
        problems: list[str] = []
        if isinstance(self.fields, list):
            if not self.fields:
                problems.append('fields: name at least one, or "any"')
            problems += _unknown_fields(self.fields)
        problems += _unknown_fields(self.not_fields)
        if len(set(self.stages)) != len(self.stages):
            problems.append("stages: each once")
        if self.every_plan and self.applying != "direct":
            problems.append("a funder in every plan takes applications directly")
        if self.applying == "automatic" and self.applications.windows:
            problems.append("an automatic award has no application windows")
        if problems:
            raise ValueError(f"{self.id}: " + "; ".join(problems))
        return self

    def funds(self, fields: list[str]) -> bool:
        """Whether it funds a programme with these field tags: one shared tag is enough, and "any"
        funds them all, unless the programme has a tag the funder rules out."""
        if set(fields) & set(self.not_fields):
            return False
        return self.fields == "any" or bool(set(fields) & set(self.fields))

    def usable_at(self, university: str) -> bool:
        return self.study_at == "any" or university in self.study_at


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
                ("who_can_apply", f.who_can_apply), ("covers", f.covers), ("obligations", f.obligations),
                ("tips", f.tips), ("warnings", f.warnings), ("at_registration", f.at_registration),
                ("income", f.income),
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


# ---------------------------------------------------------------------------------------------- campus maps

Lat = Annotated[float, Field(ge=-90, le=90)]
Lon = Annotated[float, Field(ge=-180, le=180)]
LatLon = tuple[Lat, Lon]
Ring = Annotated[list[LatLon], Field(min_length=3)]
PlaceKind = Literal["academic", "library", "admin", "residence", "health", "sport", "food", "parking", "services", "other"]

#: Every campus we map is in South Africa: a point outside this box is a mistake, not a place.
SOUTH_AFRICA = ((-35.0, 16.0), (-22.0, 33.0))


class Place(_Strict):
    """A building (with its outline) or a named point on a campus map. A name nobody has given stays None:
    the map shows the shape and never guesses what it is."""

    id: str = Field(pattern=r"^[nwr]\d+$")  # its OpenStreetMap node, way or relation
    name: str | None = None
    kind: PlaceKind = "other"
    centre: LatLon
    outline: list[LatLon] = Field(default_factory=list)  # empty for a point
    name_source: str | None = None  # set when a person named it on campus: their source


StreetKind = Literal["road", "path"]


class Street(_Strict):
    """A road around a campus or a path across it, from OpenStreetMap, drawn under the buildings so a student can
    find the way in. A name nobody gave stays None."""

    kind: StreetKind
    name: str | None = None
    line: list[LatLon] = Field(min_length=2)


class CampusMap(_Strict):
    """One campus: its outline (one or more parts), the places inside it, and the streets around and across it."""

    campus: str
    source: str
    outline: list[Ring] = Field(min_length=1)
    places: list[Place] = Field(default_factory=list)
    streets: list[Street] = Field(default_factory=list)

    @property
    def bounds(self) -> tuple[LatLon, LatLon]:
        """(south-west, north-east) around every part of the outline."""
        points = [p for ring in self.outline for p in ring]
        return (min(p[0] for p in points), min(p[1] for p in points)), (max(p[0] for p in points), max(p[1] for p in points))


class UniversityMap(_Strict):
    """A university's campus maps (backend/data/maps/<university>.yaml), from OpenStreetMap."""

    university: str
    release: bool = False
    campuses: list[CampusMap] = Field(min_length=1)
    sources: list[Source] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check(self):
        source_ids = [s.id for s in self.sources]
        problems: list[str] = []
        if len(set(source_ids)) != len(source_ids):
            problems.append("source ids must be unique")
        campus_ids = [c.campus for c in self.campuses]
        if len(set(campus_ids)) != len(campus_ids):
            problems.append("campus ids must be unique")
        (south, west), (north, east) = SOUTH_AFRICA
        for c in self.campuses:
            cited = [(f"campus '{c.campus}'", c.source)]
            cited += [(f"{c.campus}/{p.id} name", p.name_source) for p in c.places if p.name_source]
            problems += _unknown_sources(cited, source_ids)
            ids = [p.id for p in c.places]
            if len(set(ids)) != len(ids):
                problems.append(f"{c.campus}: place ids must be unique")
            points = [pt for ring in c.outline for pt in ring] + [p.centre for p in c.places]
            points += [pt for s in c.streets for pt in s.line]
            if any(not (south <= lat <= north and west <= lon <= east) for lat, lon in points):
                problems.append(f"{c.campus}: a point lies outside South Africa")
            (s, w), (n, e) = c.bounds
            pad = 0.002  # about 200 m: a building on the outline's edge
            for p in c.places:
                if not (s - pad <= p.centre[0] <= n + pad and w - pad <= p.centre[1] <= e + pad):
                    problems.append(f"{c.campus}/{p.id}: its centre lies outside the campus")
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def campus(self, campus_id: str) -> CampusMap | None:
        return next((c for c in self.campuses if c.campus == campus_id), None)

    def source(self, source_id: str) -> Source | None:
        return next((s for s in self.sources if s.id == source_id), None)


# ---------------------------------------------------------------------------------------------- colleges

CollegeKind = Literal["tvet", "private_higher_education", "private_college"]
#: "public" is a public TVET college; the others are a private institution's place in DHET's registers.
CollegeStatus = Literal["public", "registered", "provisionally_registered", "cancelled"]


class WebsiteCheck(_Strict):
    """When we last opened the website DHET lists for a college, and whether it was the college's own working
    site. A dead, parked, suspended or placeholder address is never shown as a link: anyone could buy it."""

    checked: date
    works: bool
    note: str = Field(min_length=3)  # what we found, in plain words


class College(_Strict):
    """A college as DHET lists it: a public TVET college, or a private institution in one of its registers,
    with the registration number, sites and registered qualifications exactly as printed there."""

    id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name: str = Field(min_length=2)
    kind: CollegeKind
    status: CollegeStatus
    registration_number: str | None = None  # as printed, typos included; None where the register shows none
    provinces: list[Province] = Field(default_factory=list)
    website: str | None = Field(default=None, pattern=r"^(https?://)?www\.[a-z0-9.\-]+\.[a-z]{2,}(/\S*)?$")
    website_check: WebsiteCheck | None = None
    phone: str | None = None  # a public college's office line (never a person's)
    head_office: LatLon | None = None
    sites: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)  # the register's own notes, e.g. "registered until ..."
    source: str

    @model_validator(mode="after")
    def _status_fits_kind(self):
        if (self.kind == "tvet") != (self.status == "public"):
            raise ValueError(f"{self.id}: only a public TVET college has status 'public'")
        if self.kind == "tvet" and self.registration_number:
            raise ValueError(f"{self.id}: public TVET colleges are not in the private registers")
        return self


class OccupationalQualification(_Strict):
    """A QCTO occupational qualification that public TVET colleges offer (DHET's list for the year)."""

    saqa_id: str = Field(pattern=r"^\d{4,6}$")
    code: str | None = None
    name: str
    nsfas_allowances: bool  # DHET's "NSFAS allowances" column
    colleges: list[str] = Field(default_factory=list)  # TVET college ids; empty where DHET names none
    centre_of_specialisation: list[str] = Field(default_factory=list)  # colleges where it is a Centre of Specialisation trade
    source: str


class UnregisteredCollege(_Strict):
    """An institution DHET names as illegal ("bogus"): not registered, so its qualifications aren't recognised."""

    id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name: str = Field(min_length=2)
    where: str | None = None  # as DHET puts it ("Gauteng", "Western Cape, Global")
    source: str


class CollegesPack(_Strict):
    """Colleges (backend/data/national/colleges.yaml): DHET's public TVET colleges and its registers of
    private institutions, with its warning about bogus colleges. The same rules as every pack."""

    release: bool = False
    colleges: list[College] = Field(min_length=1)
    occupational: list[OccupationalQualification] = Field(default_factory=list)
    unregistered: list[UnregisteredCollege] = Field(default_factory=list)
    warning_signs: SourcedList | None = None  # DHET's signs of a bogus college
    sources: list[Source] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check(self):
        source_ids = [s.id for s in self.sources]
        problems: list[str] = []
        if len(set(source_ids)) != len(source_ids):
            problems.append("source ids must be unique")
        ids = [c.id for c in self.colleges] + [u.id for u in self.unregistered]
        if len(set(ids)) != len(ids):
            problems.append("college ids must be unique")
        tvet = {c.id for c in self.colleges if c.kind == "tvet"}
        cited = [(c.id, c.source) for c in self.colleges] + [(u.id, u.source) for u in self.unregistered]
        cited += [(f"occupational {q.saqa_id}", q.source) for q in self.occupational]
        if self.warning_signs:
            cited.append(("warning_signs", self.warning_signs.source))
        problems += _unknown_sources(cited, source_ids)
        for q in self.occupational:
            unknown = [c for c in q.colleges + q.centre_of_specialisation if c not in tvet]
            if unknown:
                problems.append(f"occupational {q.saqa_id}: unknown TVET colleges {unknown}")
        (south, west), (north, east) = SOUTH_AFRICA
        for c in self.colleges:
            if c.head_office and not (south <= c.head_office[0] <= north and west <= c.head_office[1] <= east):
                problems.append(f"{c.id}: its head office lies outside South Africa")
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def college(self, college_id: str) -> College | None:
        return next((c for c in self.colleges if c.id == college_id), None)

    def source(self, source_id: str) -> Source | None:
        return next((s for s in self.sources if s.id == source_id), None)
