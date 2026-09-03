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


@pytest.mark.parametrize("codes", [[None, None, "00123456"], [None, None], []])
def test_sparse_or_empty_barcode_column_is_retained(codes):
    data = pd.DataFrame({"code": pd.Series(codes, dtype="string")})
    clean, report = clean_products(data)
    assert "code" in clean
    assert report.output_rows == sum(code is not None for code in codes)
    assert report.rejected_rows == sum(code is None for code in codes)


def test_normalized_column_collision_is_rejected():
    with pytest.raises(ValueError, match="duplicate names"):
        clean_products(pd.DataFrame({"code": ["12345678"], "a-b": [1], "a_b": [2]}))


def test_barcode_requires_ascii_digits_and_preserves_input():
    data = pd.DataFrame({"code": ["１２３４５６７８", " 00123456 "]})
    original = data.copy(deep=True)
    clean, report = clean_products(data)
    assert clean["code"].tolist() == ["00123456"]
    assert report.rejected_rows == 1
    pd.testing.assert_frame_equal(data, original)


def test_policy_rejects_nonpositive_barcode_length():
    with pytest.raises(ValueError, match="positive"):
        CleaningPolicy(minimum_barcode_length=0)


def test_stream_documents_independent_chunk_semantics():
    chunk = pd.DataFrame({"code": ["12345678"]})
    results = list(QualityPipeline().run_stream([chunk, chunk]))
    assert [report.output_rows for _, report in results] == [1, 1]
