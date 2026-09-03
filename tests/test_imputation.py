import pandas as pd
import pytest

from off_quality import ColumnImputer, ImputationMethod


def test_median_is_learned_only_during_fit():
    training = pd.DataFrame({"energy": [10.0, 20.0, None]})
    holdout = pd.DataFrame({"energy": [None, 1_000.0]})

    fitted = ColumnImputer(("energy",), ImputationMethod.MEDIAN).fit(training)
    transformed = fitted.transform(holdout)

    assert transformed["energy"].tolist() == [15.0, 1_000.0]


def test_imputer_rejects_schema_drift():
    fitted = ColumnImputer(("energy",), ImputationMethod.CONSTANT, 0).fit(
        pd.DataFrame({"energy": [None]})
    )

    with pytest.raises(ValueError, match="energy"):
        fitted.transform(pd.DataFrame({"fat": [1.0]}))
