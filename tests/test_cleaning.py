import pandas as pd
import pytest

from off_quality import CleaningPolicy, QualityPipeline, RejectionReason, clean_products


def test_validates_barcodes_and_removes_duplicates():
    data = pd.DataFrame({"code": ["12345678", "12345678", "invalid"], "name": ["A", "A", "B"]})
    clean, report = clean_products(data)
    assert clean["code"].tolist() == ["12345678"]
    assert report.duplicate_rows_removed == 1
    assert report.rejected_by_reason[RejectionReason.INVALID_BARCODE] == 1
    assert report.input_rows == 3
    assert report.output_rows == 1


def test_requires_barcode_column():
    with pytest.raises(ValueError, match="code"):
        clean_products(pd.DataFrame({"name": ["A"]}))


def test_policy_rejects_invalid_threshold():
    with pytest.raises(ValueError, match="between 0 and 1"):
        CleaningPolicy(max_missing_ratio=1.2)


def test_stream_preserves_chunk_boundaries():
    chunks = [
        pd.DataFrame({"code": ["12345678"], "name": ["A"]}),
        pd.DataFrame({"code": ["87654321"], "name": ["B"]}),
    ]
    results = list(QualityPipeline().run_stream(chunks))
    assert [clean["code"].item() for clean, _ in results] == ["12345678", "87654321"]


def test_report_mapping_is_immutable():
    _, report = clean_products(pd.DataFrame({"code": ["12345678"]}))
    with pytest.raises(TypeError):
        report.rejected_by_reason[RejectionReason.INVALID_BARCODE] = 2
