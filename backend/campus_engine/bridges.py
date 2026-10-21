"""The three-slot application plan: the goal, a bridge into the goal, and a safer related choice.

Bridges come only from routes a university publishes. A bridge is labelled
'by_rule' only when the university's own rules promise progression if the
conditions are met; everything else is 'considered'.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .matching import NOT_YET, REACH, TIER_RANK, UNVERIFIED, Match, assess
from .schemas import Bridge, University

GUARANTEE_RANK = {"by_rule": 0, "considered": 1}
GUARANTEE_LABELS = {
    "by_rule": "Guaranteed by the university's rules if you meet the conditions",
    "considered": "Considered, not guaranteed",
}


@dataclass
class Slot:
    number: int
    role: str  # goal | bridge | safe | route
    match: Match
    bridge: Bridge | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class Plan:
    goal: Slot
    bridge: Slot | None
    safe: Slot | None
    other_routes: list[Slot] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _bridge_notes(bridge: Bridge, uni: University) -> list[str]:
    notes = [GUARANTEE_LABELS[bridge.guarantee] + ".", f"Conditions: {bridge.conditions}"]
    if bridge.max_places:
        notes.append(f"Places on this route: {bridge.max_places}.")
    if bridge.added_years:
        years = "year" if bridge.added_years == 1 else "years"
        notes.append(f"Adds about {bridge.added_years} {years} before you start the goal programme.")
    if bridge.eligibility_note:
        notes.append(f"Eligibility: {bridge.eligibility_note}")
    return notes


def build_plan(
    catalogue: dict[str, University],
    university: str,
    goal_programme: str,
    marks: dict[str, float],
) -> Plan:
    uni = catalogue[university]
    goal = uni.programme(goal_programme)
    goal_match = assess(uni, goal, marks)
    plan_notes: list[str] = []

    # Slot 2: a programme with a published route into the goal. Routes the learner
    # can't enter yet go last, then routes with eligibility restrictions (we never ask
    # learners about protected characteristics, so they decide for themselves), then
    # rule-based guarantees before considered ones, then the learner's tier.
    candidates = []
    for p in uni.programmes:
        for b in p.bridges_to:
            if b.to != goal.id:
                continue
            m = assess(uni, p, marks)
            key = (
                m.tier == NOT_YET,
                b.eligibility_note is not None,
                GUARANTEE_RANK[b.guarantee],
                TIER_RANK[m.tier],
                -(b.max_places or 0),
                p.id,
            )
            candidates.append((key, m, b))
    candidates.sort(key=lambda c: c[0])

    bridge_slot = None
    other_routes: list[Slot] = []
    if candidates:
        _, m, b = candidates[0]
        bridge_slot = Slot(2, "bridge", m, b, _bridge_notes(b, uni) + m.explanation)
        other_routes = [Slot(0, "route", m2, b2, _bridge_notes(b2, uni) + m2.explanation) for _, m2, b2 in candidates[1:]]
    else:
        plan_notes.append(f"No published route into {goal.name} is in our data yet.")

    # Slot 3: the related programme where the learner stands best, across all universities.
    used = {(uni.university, goal.id)}
    if bridge_slot:
        used.add((uni.university, bridge_slot.match.programme_id))
    goal_fields = set(goal.fields)
    safe_candidates = []
    for u in catalogue.values():
        for p in u.programmes:
            if (u.university, p.id) in used or not goal_fields & set(p.fields):
                continue
            m = assess(u, p, marks)
            if m.tier == NOT_YET:
                continue
            safe_candidates.append(((TIER_RANK[m.tier], p.selective, u.university, p.id), m))
    safe_candidates.sort(key=lambda c: c[0])

    safe_slot = None
    if safe_candidates:
        m = safe_candidates[0][1]
        notes = list(m.explanation)
        if m.tier in (REACH, UNVERIFIED):
            notes.append(
                "This is not a safe choice yet. Add a less selective option once more universities are verified."
            )
        safe_slot = Slot(3, "safe", m, notes=notes)
    else:
        plan_notes.append("No related programme you currently qualify for is in our data yet.")

    if uni.max_choices is None:
        plan_notes.append(f"Check how many programmes {uni.name} lets you list on one application.")
    else:
        at_goal_uni = 1 + (bridge_slot is not None) + (
            safe_slot is not None and safe_slot.match.university == uni.university
        )
        if at_goal_uni > uni.max_choices:
            plan_notes.append(
                f"{uni.name} allows {uni.max_choices} choice(s) per application, so put one of these at another university."
            )

    return Plan(
        goal=Slot(1, "goal", goal_match, notes=list(goal_match.explanation)),
        bridge=bridge_slot,
        safe=safe_slot,
        other_routes=other_routes,
        notes=plan_notes,
    )
