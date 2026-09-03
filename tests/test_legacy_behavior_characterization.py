from dataclasses import dataclass

import pandas as pd
import pytest

from off_quality import (
    CleaningPolicy,
    ColumnImputer,
    DataProfiler,
    ImputationMethod,
    QualityDimension,
    QualityPipeline,
    RejectionReason,
    missingness,
)
from off_quality.pipeline import RuleResult


def test_raw_cleaning_order_threshold_survivor_and_counts() -> None:
    frame = pd.DataFrame(
        {
            " code ": [" 12345678 ", "12345678", "bad"],
            "keep-at-limit": [1.0, None, 3.0],
            "drop-above-limit": [1.0, None, None],
        }
    )
    original = frame.copy(deep=True)

    cleaned, report = QualityPipeline(CleaningPolicy(max_missing_ratio=1 / 3)).run(frame)

    assert cleaned.to_dict(orient="records") == [
        {"code": "12345678", "keep_at_limit": 1.0}
    ]
    assert report.rejected_by_reason == {
        RejectionReason.INVALID_BARCODE: 1,
        RejectionReason.DUPLICATE_BARCODE: 1,
    }
    pd.testing.assert_frame_equal(frame, original)


def test_custom_rules_keep_order_and_aggregate_rejections() -> None:
    calls: list[str] = []

    @dataclass(frozen=True)
    class RecordingRule:
        name: str

        def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult:
            del policy
            calls.append(self.name)
            return RuleResult(frame, RejectionReason.INVALID_BARCODE, 2)

    pipeline = QualityPipeline(rules=(RecordingRule("first"), RecordingRule("second")))
    _, report = pipeline.run(pd.DataFrame({"code": ["12345678"]}))

    assert calls == ["first", "second"]
    assert report.rejected_by_reason[RejectionReason.INVALID_BARCODE] == 4


def test_missingness_returns_labelled_descending_ratios() -> None:
    frame = pd.DataFrame({"complete": [1, 2], "empty": [None, None], "half": [1, None]})

    ratios = missingness(frame)

    assert ratios.index.tolist() == ["empty", "half", "complete"]
    assert ratios.tolist() == [1.0, 0.5, 0.0]


@pytest.mark.parametrize(
    ("method", "constant", "expected"),
    [
        (ImputationMethod.MOST_FREQUENT, None, "apple"),
        (ImputationMethod.CONSTANT, "missing", "missing"),
    ],
)
def test_uncovered_imputation_branches_preserve_input_and_other_columns(
    method: ImputationMethod, constant: object, expected: object
) -> None:
    training = pd.DataFrame({"label": ["apple", "apple", None]})
    holdout = pd.DataFrame({"label": [None], "untouched": [7]})
    original = holdout.copy(deep=True)

    fitted = ColumnImputer(("label",), method, constant).fit(training)
    transformed = fitted.transform(holdout)

    assert transformed.loc[0, "label"] == expected
    assert transformed.loc[0, "untouched"] == 7
    pd.testing.assert_frame_equal(holdout, original)


def test_profiler_zero_denominators_and_column_order() -> None:
    profile = DataProfiler().profile(pd.DataFrame(columns=["energy", "name"]))

    assert [column.name for column in profile.columns] == ["energy", "name"]
    scores = {metric.dimension: metric.score for metric in profile.scorecard}
    assert scores == {
        QualityDimension.COMPLETENESS: 1.0,
        QualityDimension.UNIQUENESS: 1.0,
    }
