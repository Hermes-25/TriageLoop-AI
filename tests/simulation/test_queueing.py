import unittest

from triageloop.queueing import PatientTemplate, QueueTask, _apply_updates, policy_key, queue_snapshot


def task(
    identifier: str,
    *,
    arrival: float = 0,
    deadline: float = 60,
    level: int = 3,
    risk: float = 0.05,
    uncertain: bool = False,
    updates=(),
) -> QueueTask:
    template = PatientTemplate(
        template_id=f"T-{identifier}",
        static_level=level,
        critical=False,
        deterioration_signal_minutes=None,
        true_deadline_minutes=deadline,
        initial_predicted_deadline_minutes=deadline,
        initial_risk_30m=risk,
        initial_hard_rule=False,
        initial_uncertain=uncertain,
        updates=tuple(updates),
        age_group="adult",
        history_status="none",
    )
    return QueueTask(
        task_id=identifier,
        template=template,
        arrival=arrival,
        queue_entry=arrival,
        service_duration=10,
        space_duration=0,
        resource="reassessment",
        space="none",
        predicted_deadline=arrival + deadline,
        risk_30m=risk,
        hard_rule=False,
        uncertain=uncertain,
    )


class QueuePolicyTests(unittest.TestCase):
    def test_deterioration_update_moves_patient_ahead(self) -> None:
        deteriorating = task("deteriorating", deadline=100, updates=((10, 20, 0.8, False, False),))
        stable = task("stable", deadline=40)
        self.assertGreater(policy_key(deteriorating, "triageloop", 0), policy_key(stable, "triageloop", 0))
        _apply_updates(deteriorating, 10, "triageloop")
        self.assertLess(policy_key(deteriorating, "triageloop", 10), policy_key(stable, "triageloop", 10))

    def test_uncertainty_breaks_an_equal_priority_tie(self) -> None:
        uncertain = task("uncertain", uncertain=True)
        certain = task("certain", uncertain=False)
        self.assertLess(policy_key(uncertain, "triageloop", 0), policy_key(certain, "triageloop", 0))

    def test_absolute_deadline_ages_older_patient(self) -> None:
        older = task("older", arrival=0, deadline=60)
        younger = task("younger", arrival=20, deadline=60)
        self.assertLess(policy_key(older, "triageloop", 30), policy_key(younger, "triageloop", 30))

    def test_snapshot_exposes_negative_clinical_slack(self) -> None:
        urgent = task("urgent", deadline=5)
        snapshot = queue_snapshot([urgent], [20], "triageloop", 0)
        self.assertEqual(snapshot["items"][0]["predicted_time_to_action_minutes"], 20)
        self.assertEqual(snapshot["items"][0]["clinical_slack_minutes"], -15)
        self.assertTrue(snapshot["items"][0]["capacity_conflict"])

    def test_periodic_retriage_waits_for_next_fifteen_minute_sweep(self) -> None:
        deteriorating = task("periodic", deadline=120, level=4, updates=((7, 20, 0.9, True, False),))
        deteriorating.template = PatientTemplate(
            **{**deteriorating.template.__dict__, "update_rule_levels": (1,)}
        )
        _apply_updates(deteriorating, 14, "static_periodic")
        self.assertEqual(deteriorating.next_update_index, 0)
        _apply_updates(deteriorating, 15, "static_periodic")
        self.assertEqual(deteriorating.next_update_index, 1)
        self.assertEqual(deteriorating.periodic_level, 1)
        self.assertTrue(deteriorating.hard_rule)

    def test_periodic_retriage_does_not_use_model_risk_or_uncertainty(self) -> None:
        periodic = task("periodic", level=4, risk=0.95, uncertain=True)
        self.assertEqual(policy_key(periodic, "static_periodic", 30), (1.0, 4.0, 0))


if __name__ == "__main__":
    unittest.main()
