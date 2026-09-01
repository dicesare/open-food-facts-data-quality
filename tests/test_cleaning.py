import pandas as pd
import pytest

from off_quality import clean_products


def test_validates_barcodes_and_removes_duplicates():
    data = pd.DataFrame({"code": ["12345678", "12345678", "invalid"], "name": ["A", "A", "B"]})
    clean, report = clean_products(data)
    assert clean["code"].tolist() == ["12345678"]
    assert report.duplicate_rows_removed == 1


def test_requires_barcode_column():
    with pytest.raises(ValueError, match="code"):
        clean_products(pd.DataFrame({"name": ["A"]}))
