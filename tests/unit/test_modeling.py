import unittest

import numpy as np

from triageloop.modeling import BoostedHazard, LogisticHazard
from triageloop.uncertainty import MondrianConformal, OODDetector


class ModelingTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(42)
        self.x = rng.normal(size=(300, 3))
        self.y = (self.x[:, 0] + 0.5 * self.x[:, 1] > 0).astype(float)

    def test_logistic_learns_ordered_risk(self) -> None:
        model = LogisticHazard().fit(self.x, self.y)
        score = model.decision_function(np.asarray([[-2, 0, 0], [2, 0, 0]]))
        self.assertLess(score[0], score[1])

    def test_boosted_round_trip_is_exact(self) -> None:
        model = BoostedHazard(estimators=8).fit(self.x, self.y)
        restored = BoostedHazard.from_dict(model.to_dict())
        np.testing.assert_allclose(model.decision_function(self.x), restored.decision_function(self.x))

    def test_conformal_returns_supported_labels(self) -> None:
        probabilities = np.column_stack([np.linspace(0.01, 0.99, len(self.y))] * 4)
        labels = np.column_stack([self.y] * 4)
        conformal = MondrianConformal().fit(probabilities, labels)
        sets = conformal.prediction_sets(probabilities[:5])
        self.assertTrue(all(set(label_set).issubset({"critical", "non_critical"}) for row in sets for label_set in row))

    def test_ood_detector_flags_extreme_vector(self) -> None:
        detector = OODDetector().fit(self.x)
        self.assertTrue(detector.predict(np.asarray([[20.0, 20.0, 20.0]]))[0])


if __name__ == "__main__":
    unittest.main()
