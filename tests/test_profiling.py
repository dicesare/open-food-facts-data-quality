import pandas as pd
import pytest

from off_quality import DataProfiler, QualityDimension


def test_profile_exposes_aggregate_quality_evidence():
    data = pd.DataFrame({"code": ["1", "1", "2"], "energy": [10.0, None, 30.0]})

    profile = DataProfiler().profile(data)

    assert profile.rows == 3
    assert profile.columns[1].missing_ratio == pytest.approx(1 / 3)
    scores = {metric.dimension: metric.score for metric in profile.scorecard}
    assert scores[QualityDimension.COMPLETENESS] == pytest.approx(5 / 6)
    assert scores[QualityDimension.UNIQUENESS] == pytest.approx(2 / 3)
