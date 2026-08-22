import unittest

import numpy as np

from triageloop.curated import build_curated_cases
from triageloop.features import FeatureTransformer, extract_features, feature_names
from triageloop.schemas import PatientState


class FeatureTests(unittest.TestCase):
    def test_feature_width_is_stable(self) -> None:
        case = build_curated_cases()[8]
        patient = PatientState.model_validate(case["patient"])
        self.assertEqual(len(extract_features(patient)), len(feature_names()))
        self.assertEqual(len(feature_names()), len(set(feature_names())))

    def test_early_snapshot_does_not_see_future_observation(self) -> None:
        case = build_curated_cases()[8]
        patient = PatientState.model_validate(case["patient"])
        early_before = extract_features(patient, 0)
        changed_future = patient.model_copy(deep=True)
        changed_future.observations[-1].values.heart_rate_bpm = 250
        early_after = extract_features(changed_future, 0)
        np.testing.assert_array_equal(early_before, early_after)

    def test_transformer_imputes_missing_values(self) -> None:
        transformer = FeatureTransformer.create().fit(np.asarray([[1.0, np.nan], [3.0, 2.0]]))
        transformed = transformer.transform(np.asarray([[np.nan, np.nan]]))
        self.assertTrue(np.all(np.isfinite(transformed)))


if __name__ == "__main__":
    unittest.main()
