import inspect
from typing import get_type_hints

import pandas as pd

import off_quality
from off_quality import DataProfiler, QualityPipeline, clean_products, missingness
from off_quality.domain import CleaningReport
from off_quality.profiling import DatasetProfile

EXPECTED_PUBLIC_API = {
    "CleaningPolicy",
    "CleaningReport",
    "ColumnImputer",
    "ColumnProfile",
    "DataProfiler",
    "DatasetProfile",
    "FittedColumnImputer",
    "ImputationMethod",
    "QualityDimension",
    "QualityMetric",
    "QualityPipeline",
    "RejectionReason",
    "clean_products",
    "missingness",
}


def test_public_api_exports_are_characterized() -> None:
    assert set(off_quality.__all__) == EXPECTED_PUBLIC_API
    clean_signature = inspect.signature(clean_products)
    run_signature = inspect.signature(QualityPipeline.run)
    profile_signature = inspect.signature(DataProfiler.profile)

    assert tuple(clean_signature.parameters) == ("data", "max_missing")
    assert clean_signature.parameters["max_missing"].default == 0.6
    assert tuple(run_signature.parameters) == ("self", "frame")
    assert tuple(profile_signature.parameters) == ("self", "frame", "key")
    assert profile_signature.parameters["key"].default == "code"

    assert get_type_hints(clean_products) == {
        "data": pd.DataFrame,
        "max_missing": float,
        "return": tuple[pd.DataFrame, CleaningReport],
    }
    assert get_type_hints(QualityPipeline.run) == {
        "frame": pd.DataFrame,
        "return": tuple[pd.DataFrame, CleaningReport],
    }
    assert get_type_hints(DataProfiler.profile) == {
        "frame": pd.DataFrame,
        "key": str,
        "return": DatasetProfile,
    }


def test_raw_frame_entry_points_have_no_evidence_provenance() -> None:
    frame = pd.DataFrame({"code": ["12345678"], "energy": [None]})

    cleaned, report = clean_products(frame)
    profile = DataProfiler().profile(frame)
    ratios = missingness(frame)

    assert isinstance(cleaned, pd.DataFrame)
    assert isinstance(ratios, pd.Series)
    for legacy_result in (cleaned, report, profile, ratios):
        assert not hasattr(legacy_result, "evidence_status")
        assert not hasattr(legacy_result, "population_ref")
        assert not hasattr(legacy_result, "run_context")


def test_pipeline_preserves_input_and_returns_a_fresh_frame() -> None:
    frame = pd.DataFrame({"code": [" 00123456 "], "energy": [None]})
    original = frame.copy(deep=True)

    cleaned, _ = QualityPipeline().run(frame)

    pd.testing.assert_frame_equal(frame, original)
    assert cleaned is not frame
    assert cleaned["code"].tolist() == ["00123456"]
