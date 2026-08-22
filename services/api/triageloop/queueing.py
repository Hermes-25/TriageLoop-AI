"""Minute-resolution discrete-event Queue Twin and scheduling policies."""

from __future__ import annotations

from dataclasses import dataclass, replace
import heapq
import json
from pathlib import Path
from typing import Iterable, Literal

import numpy as np

from .features import event_minute, load_encounters
from .metrics import roc_auc
from .recommendation import ModelBundle, RecommendedAction, recommend
from .safety import MAX_WAIT_MINUTES, evaluate_safety
from .schemas import SyntheticEncounter


SIMULATION_VERSION = "1.2.0"
RISK_PROMOTION_THRESHOLD = 0.20
PolicyName = Literal["fifo", "static", "static_periodic", "triageloop"]


@dataclass(frozen=True)
class SiteProfile:
    name: str
    visits_per_day: int
    triage_nurses: int
    reassessment_nurses: int
    clinicians: int
    monitored_spaces: int
    treatment_spaces: int


@dataclass(frozen=True)
class PatientTemplate:
    template_id: str
    static_level: int
    critical: bool
    deterioration_signal_minutes: float | None
    true_deadline_minutes: float
    initial_predicted_deadline_minutes: float
    initial_risk_30m: float
    initial_hard_rule: bool
    initial_uncertain: bool
    updates: tuple[tuple[float, float, float, bool, bool], ...]
    age_group: str
    history_status: str
    update_rule_levels: tuple[int, ...] = ()


@dataclass
class QueueTask:
    task_id: str
    template: PatientTemplate
    arrival: float
    queue_entry: float
    service_duration: float
    space_duration: float
    resource: Literal["clinician", "reassessment"]
    space: Literal["monitored", "treatment", "none"]
    predicted_deadline: float
    risk_30m: float
    hard_rule: bool
    uncertain: bool
    periodic_level: int | None = None
    next_update_index: int = 0
    start: float | None = None
    initial_clinical_slack: float | None = None
    alerts: int = 0
    alerts_in_shift: int = 0

    @property
    def static_level(self) -> int:
        return self.template.static_level

    @property
    def critical(self) -> bool:
        return self.template.critical

    @property
    def true_deadline(self) -> float:
        return self.arrival + self.template.true_deadline_minutes


@dataclass
class SimulationResult:
    seed: int
    site: str
    load_state: str
    policy: PolicyName
    arrivals: int
    critical_cases: int
    action_window_miss_rate: float
    unsafe_undertriage_rate: float
    critical_recall: float
    mean_signal_to_action_minutes: float
    negative_slack_minutes: float
    median_wait_minutes: float
    low_acuity_p90_wait_minutes: float
    waiting_time_effectiveness: float
    rank_triage_effectiveness: float
    throughput_within_shift: float
    max_queue_length: int
    capacity_conflict_rate: float
    consolidated_alerts: int
    alerts_per_waiting_patient_hour: float
    alerts_per_reassessment_nurse_hour: float
    utilization: dict[str, float]


def load_site_profiles(path: Path) -> tuple[dict[str, SiteProfile], int, dict[str, float], int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    profiles = {
        name: SiteProfile(name=name, **values)
        for name, values in payload["profiles"].items()
    }
    return profiles, int(payload["shift_minutes"]), {name: float(value) for name, value in payload["load_states"].items()}, int(payload["deterioration_response_minutes"])


def build_template_library(
    encounters: Iterable[SyntheticEncounter],
    bundle: ModelBundle,
    deterioration_response_minutes: int = 10,
) -> list[PatientTemplate]:
    templates = []
    for encounter in encounters:
        if encounter.truth.split != "test":
            continue
        patient = encounter.patient
        updates = []
        update_rule_levels = []
        initial_action = None
        for index, observation in enumerate(patient.observations):
            prefix = patient.model_copy(update={"observations": patient.observations[: index + 1]})
            result = recommend(prefix, bundle, evaluated_at=observation.recorded_at)
            elapsed = (observation.recorded_at - patient.arrival_time).total_seconds() / 60
            absolute_deadline = elapsed + result.action_window.maximum_minutes
            hard = result.recommended_action == RecommendedAction.IMMEDIATE_REVIEW
            uncertain = result.uncertainty.state.value in {"moderate", "high"}
            if index == 0:
                initial_action = (absolute_deadline, float(result.risk_by_horizon["30"]), hard, uncertain)
            else:
                updates.append((elapsed, absolute_deadline, float(result.risk_by_horizon["30"]), hard, uncertain))
                update_rule_levels.append(evaluate_safety(prefix, evaluated_at=observation.recorded_at).recommended_level)
        event = event_minute(encounter)
        true_deadline = float(event + deterioration_response_minutes if event is not None else MAX_WAIT_MINUTES[patient.clinician_state.assigned_level])
        hard_deadlines = ([5.0] if initial_action[2] else []) + [elapsed + 5.0 for elapsed, _deadline, _risk, hard, _uncertain in updates if hard]
        if hard_deadlines:
            true_deadline = min(true_deadline, min(hard_deadlines))
        templates.append(
            PatientTemplate(
                template_id=encounter.encounter_id,
                static_level=patient.clinician_state.assigned_level,
                critical=event is not None,
                deterioration_signal_minutes=float(event) if event is not None else None,
                true_deadline_minutes=true_deadline,
                initial_predicted_deadline_minutes=float(initial_action[0]),
                initial_risk_30m=float(initial_action[1]),
                initial_hard_rule=bool(initial_action[2]),
                initial_uncertain=bool(initial_action[3]),
                updates=tuple(updates),
                age_group="pediatric" if patient.age_years < 12 else "geriatric" if patient.age_years >= 65 else "adult",
                history_status=patient.history_status.value,
                update_rule_levels=tuple(update_rule_levels),
            )
        )
    return templates


def _triage_finish_times(arrivals: np.ndarray, nurses: int, durations: np.ndarray) -> np.ndarray:
    availability = [0.0] * nurses
    heapq.heapify(availability)
    finishes = np.empty(len(arrivals))
    for index, arrival in enumerate(arrivals):
        available = heapq.heappop(availability)
        finish = max(float(arrival), available) + float(durations[index])
        finishes[index] = finish
        heapq.heappush(availability, finish)
    return finishes


def create_shift(
    profile: SiteProfile,
    load_multiplier: float,
    shift_minutes: int,
    templates: list[PatientTemplate],
    seed: int,
) -> tuple[list[QueueTask], float]:
    rng = np.random.default_rng(seed)
    expected = profile.visits_per_day * (shift_minutes / 1440) * load_multiplier
    count = max(1, int(rng.poisson(expected)))
    arrivals = np.sort(rng.uniform(0, shift_minutes, size=count))
    triage_durations = rng.uniform(2, 5, size=count)
    queue_entries = _triage_finish_times(arrivals, profile.triage_nurses, triage_durations)
    choices = rng.integers(0, len(templates), size=count)
    tasks = []
    for index, template_index in enumerate(choices):
        template = templates[int(template_index)]
        clinician_task = template.critical or template.static_level <= 3
        resource = "clinician" if clinician_task else "reassessment"
        service = float(rng.uniform(10, 18) if clinician_task else rng.uniform(5, 9))
        space = "monitored" if clinician_task and (template.critical or template.static_level <= 2) else "treatment" if clinician_task else "none"
        space_duration = float(rng.uniform(45, 95) if space == "monitored" else rng.uniform(25, 65) if space == "treatment" else 0)
        arrival = float(arrivals[index])
        tasks.append(
            QueueTask(
                task_id=f"S{seed}-P{index:04d}",
                template=template,
                arrival=arrival,
                queue_entry=float(queue_entries[index]),
                service_duration=service,
                space_duration=space_duration,
                resource=resource,
                space=space,
                predicted_deadline=arrival + template.initial_predicted_deadline_minutes,
                risk_30m=template.initial_risk_30m,
                hard_rule=template.initial_hard_rule,
                uncertain=template.initial_uncertain,
                periodic_level=template.static_level,
                alerts=0,
            )
        )
    triage_utilization = min(1.0, float(np.sum(triage_durations)) / (profile.triage_nurses * shift_minutes))
    return tasks, triage_utilization


def policy_key(task: QueueTask, policy: PolicyName, now: float) -> tuple[float, ...]:
    hard = 0.0 if task.hard_rule else 1.0
    if policy == "fifo":
        return hard, task.arrival
    if policy == "static":
        return hard, float(task.static_level), task.arrival
    if policy == "static_periodic":
        return hard, float(task.periodic_level or task.static_level), task.arrival
    # Living Acuity may promote, never demote, the clinician category. Absolute
    # category/model deadlines order equal dynamic levels, so elapsed waiting time
    # continuously erodes slack without allowing younger arrivals to reset the bound.
    dynamic_level = task.static_level
    remaining = task.predicted_deadline - now
    if task.next_update_index > 0 and task.risk_30m >= RISK_PROMOTION_THRESHOLD:
        dynamic_level = min(dynamic_level, 2)
    elif task.uncertain and remaining <= 10:
        dynamic_level = min(dynamic_level, 3)
    uncertainty_rank = 0.0 if task.uncertain else 1.0
    return hard, float(dynamic_level), task.predicted_deadline, -task.risk_30m, uncertainty_rank, task.arrival


def project_queue(
    waiting: list[QueueTask],
    server_availability: list[float],
    policy: PolicyName,
    now: float,
) -> dict[str, tuple[float, float]]:
    servers = list(server_availability)
    heapq.heapify(servers)
    projection = {}
    for task in sorted(waiting, key=lambda item: policy_key(item, policy, now)):
        available = heapq.heappop(servers)
        start = max(now, available)
        projection[task.task_id] = (start - now, task.predicted_deadline - start)
        heapq.heappush(servers, start + task.service_duration)
    return projection


def queue_snapshot(
    waiting: list[QueueTask],
    server_availability: list[float],
    policy: PolicyName,
    now: float,
) -> dict[str, object]:
    """Return the product-facing ETA/Clinical Slack view for one resource queue."""
    projection = project_queue(waiting, server_availability, policy, now)
    ordered = sorted(waiting, key=lambda task: projection[task.task_id][0])
    return {
        "simulation_version": SIMULATION_VERSION,
        "as_of_minute": now,
        "policy": policy,
        "items": [
            {
                "task_id": task.task_id,
                "patient_template_id": task.template.template_id,
                "predicted_time_to_action_minutes": round(projection[task.task_id][0], 3),
                "action_deadline_minute": round(task.predicted_deadline, 3),
                "clinical_slack_minutes": round(projection[task.task_id][1], 3),
                "capacity_conflict": projection[task.task_id][1] < 0,
                "static_level": task.static_level,
                "risk_30m": task.risk_30m,
                "uncertain": task.uncertain,
            }
            for task in ordered
        ],
    }


def _apply_updates(task: QueueTask, now: float, policy: PolicyName, alert_cutoff_minute: float = float("inf")) -> None:
    if policy == "static_periodic":
        if int(now) % 15 != 0:
            return
        while task.next_update_index < len(task.template.updates):
            elapsed, _deadline, _risk_30m, hard, _uncertain = task.template.updates[task.next_update_index]
            if task.arrival + elapsed > now:
                break
            rule_level = (
                task.template.update_rule_levels[task.next_update_index]
                if task.next_update_index < len(task.template.update_rule_levels)
                else task.static_level
            )
            task.periodic_level = min(task.periodic_level or task.static_level, rule_level)
            task.hard_rule = task.hard_rule or hard
            task.predicted_deadline = min(
                task.predicted_deadline,
                task.arrival + MAX_WAIT_MINUTES[task.periodic_level],
            )
            task.next_update_index += 1
        return
    if policy != "triageloop":
        return
    while task.next_update_index < len(task.template.updates):
        elapsed, deadline_from_arrival, risk_30m, hard, uncertain = task.template.updates[task.next_update_index]
        if task.arrival + elapsed > now:
            break
        previous = task.predicted_deadline
        task.predicted_deadline = min(task.predicted_deadline, task.arrival + deadline_from_arrival)
        task.risk_30m = max(task.risk_30m, risk_30m)
        task.hard_rule = task.hard_rule or hard
        task.uncertain = task.uncertain or uncertain
        if task.predicted_deadline < previous or hard:
            task.alerts += 1
            if now <= alert_cutoff_minute:
                task.alerts_in_shift += 1
        task.next_update_index += 1


def _available_for_task(task: QueueTask, monitored: list[float], treatment: list[float], now: float) -> bool:
    if task.space == "none":
        return True
    pool = monitored if task.space == "monitored" else treatment
    return bool(pool and pool[0] <= now)


def simulate_shift(
    source_tasks: list[QueueTask],
    profile: SiteProfile,
    shift_minutes: int,
    load_state: str,
    policy: PolicyName,
    seed: int,
    triage_utilization: float,
) -> SimulationResult:
    tasks = [replace(task) for task in source_tasks]
    if policy == "static_periodic":
        for task in tasks:
            task.predicted_deadline = task.arrival + MAX_WAIT_MINUTES[task.static_level]
            task.risk_30m = 0.0
            task.uncertain = False
            task.periodic_level = task.static_level
    pending = sorted(tasks, key=lambda item: item.queue_entry)
    waiting: list[QueueTask] = []
    clinician = [0.0] * profile.clinicians
    reassessment = [0.0] * profile.reassessment_nurses
    monitored = [0.0] * profile.monitored_spaces
    treatment = [0.0] * profile.treatment_spaces
    for pool in (clinician, reassessment, monitored, treatment):
        heapq.heapify(pool)
    index = 0
    max_queue = 0
    busy = {"clinician": 0.0, "reassessment": 0.0, "monitored_space": 0.0, "treatment_space": 0.0}
    horizon = shift_minutes + 900

    for minute in range(horizon + 1):
        now = float(minute)
        newly_added = []
        while index < len(pending) and pending[index].queue_entry <= now:
            waiting.append(pending[index])
            newly_added.append(pending[index])
            index += 1
        for task in waiting:
            _apply_updates(task, now, policy, float(shift_minutes))
        if newly_added:
            for resource_name, servers in (("clinician", clinician), ("reassessment", reassessment)):
                resource_waiting = [task for task in waiting if task.resource == resource_name]
                if resource_waiting:
                    projection = project_queue(resource_waiting, servers, policy, now)
                    for task in newly_added:
                        if task.resource == resource_name:
                            task.initial_clinical_slack = projection[task.task_id][1]
                            if policy == "triageloop" and task.initial_clinical_slack < 0:
                                task.alerts += 1
                                if now <= shift_minutes:
                                    task.alerts_in_shift += 1

        while reassessment and reassessment[0] <= now:
            candidates = [task for task in waiting if task.resource == "reassessment"]
            if not candidates:
                break
            task = min(candidates, key=lambda item: policy_key(item, policy, now))
            waiting.remove(task)
            heapq.heappop(reassessment)
            task.start = now
            finish = now + task.service_duration
            heapq.heappush(reassessment, finish)
            busy["reassessment"] += max(0.0, min(finish, shift_minutes) - min(now, shift_minutes))

        while clinician and clinician[0] <= now:
            candidates = [task for task in waiting if task.resource == "clinician" and _available_for_task(task, monitored, treatment, now)]
            if not candidates:
                break
            task = min(candidates, key=lambda item: policy_key(item, policy, now))
            waiting.remove(task)
            heapq.heappop(clinician)
            task.start = now
            finish = now + task.service_duration
            heapq.heappush(clinician, finish)
            busy["clinician"] += max(0.0, min(finish, shift_minutes) - min(now, shift_minutes))
            if task.space != "none":
                pool = monitored if task.space == "monitored" else treatment
                heapq.heappop(pool)
                release = now + task.space_duration
                heapq.heappush(pool, release)
                key = "monitored_space" if task.space == "monitored" else "treatment_space"
                busy[key] += max(0.0, min(release, shift_minutes) - min(now, shift_minutes))

        max_queue = max(max_queue, len(waiting))
        if index == len(pending) and not waiting:
            break

    fallback_start = float(horizon)
    starts = np.asarray([task.start if task.start is not None else fallback_start for task in tasks])
    arrivals = np.asarray([task.arrival for task in tasks])
    waits = starts - arrivals
    critical = np.asarray([task.critical for task in tasks])
    true_deadlines = np.asarray([task.true_deadline for task in tasks])
    misses = starts > true_deadlines
    low_acuity = np.asarray([task.static_level >= 4 for task in tasks])
    signal_times = np.asarray([task.arrival + (task.template.deterioration_signal_minutes or task.template.true_deadline_minutes) for task in tasks])
    signal_delay = np.maximum(0, starts - signal_times)
    windows = np.asarray([max(1.0, task.template.true_deadline_minutes) for task in tasks])
    conflict = np.asarray([(task.initial_clinical_slack or 0) < 0 for task in tasks])
    total_wait_hours = max(1e-6, float(np.sum(waits)) / 60)
    utilization = {
        "triage_nurse": triage_utilization,
        "reassessment_nurse": min(1.0, busy["reassessment"] / (profile.reassessment_nurses * shift_minutes)),
        "clinician": min(1.0, busy["clinician"] / (profile.clinicians * shift_minutes)),
        "monitored_space": min(1.0, busy["monitored_space"] / (profile.monitored_spaces * shift_minutes)),
        "treatment_space": min(1.0, busy["treatment_space"] / (profile.treatment_spaces * shift_minutes)),
    }
    critical_count = int(np.sum(critical))
    miss_rate = float(np.mean(misses[critical])) if critical_count else 0.0
    undertriage_mask = critical & np.asarray([task.static_level >= 3 for task in tasks])
    undertriage_rate = float(np.mean(misses[undertriage_mask])) if np.any(undertriage_mask) else 0.0
    consolidated_alerts = sum(task.alerts_in_shift for task in tasks) if policy == "triageloop" else 0
    reassessment_nurse_hours = profile.reassessment_nurses * (shift_minutes / 60)
    return SimulationResult(
        seed=seed,
        site=profile.name,
        load_state=load_state,
        policy=policy,
        arrivals=len(tasks),
        critical_cases=critical_count,
        action_window_miss_rate=miss_rate,
        unsafe_undertriage_rate=undertriage_rate,
        critical_recall=1 - miss_rate,
        mean_signal_to_action_minutes=float(np.mean(signal_delay[critical])) if critical_count else 0.0,
        negative_slack_minutes=float(np.sum(np.maximum(0, starts[critical] - true_deadlines[critical]))),
        median_wait_minutes=float(np.median(waits)),
        low_acuity_p90_wait_minutes=float(np.quantile(waits[low_acuity], 0.9)) if np.any(low_acuity) else 0.0,
        waiting_time_effectiveness=float(np.mean(np.maximum(0, 1 - waits / windows))),
        rank_triage_effectiveness=roc_auc(critical.astype(float), -waits),
        throughput_within_shift=float(np.mean(starts <= shift_minutes)),
        max_queue_length=max_queue,
        capacity_conflict_rate=float(np.mean(conflict)),
        consolidated_alerts=consolidated_alerts,
        alerts_per_waiting_patient_hour=float(sum(task.alerts for task in tasks) / total_wait_hours) if policy == "triageloop" else 0.0,
        alerts_per_reassessment_nurse_hour=(consolidated_alerts / reassessment_nurse_hours) if policy == "triageloop" else 0.0,
        utilization=utilization,
    )
