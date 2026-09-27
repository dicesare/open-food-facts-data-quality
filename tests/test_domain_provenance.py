import dataclasses

import pandas as pd
import pytest


def test_t_foundation_domain_01_population_id():
    """T-FOUNDATION-DOMAIN-01: PopulationId contains the two architecture-defined population IDs."""
    from off_quality.domain import PopulationId

    assert hasattr(PopulationId, "HISTORICAL_2017_RAW_PARSE")
    assert hasattr(PopulationId, "HISTORICAL_2017_CORRECTED")

    assert PopulationId.HISTORICAL_2017_RAW_PARSE == "HISTORICAL_2017_RAW_PARSE"
    assert PopulationId.HISTORICAL_2017_CORRECTED == "HISTORICAL_2017_CORRECTED"


def test_t_foundation_domain_02_population_ref():
    """T-FOUNDATION-DOMAIN-02: PopulationRef is a frozen provenance value object with exact fields."""
    from off_quality.domain import PopulationId, PopulationRef

    assert dataclasses.is_dataclass(PopulationRef)
    assert PopulationRef.__dataclass_params__.frozen is True

    fields = {f.name: f.type for f in dataclasses.fields(PopulationRef)}
    expected_fields = {"population_id", "archive_sha256", "parser_spec_sha256", "rows", "columns"}
    assert set(fields.keys()) == expected_fields

    ref = PopulationRef(
        population_id=PopulationId.HISTORICAL_2017_RAW_PARSE,
        archive_sha256="a"*64,
        parser_spec_sha256="b"*64,
        rows=10,
        columns=5
    )
    assert ref.rows == 10

    with pytest.raises(dataclasses.FrozenInstanceError):
        ref.rows = 20


def test_t_foundation_domain_03_population_frame():
    """T-FOUNDATION-DOMAIN-03: PopulationFrame pairs a DataFrame with PopulationRef without claiming deep immutability or security boundary."""
    from off_quality.domain import PopulationFrame, PopulationId, PopulationRef

    ref = PopulationRef(
        population_id=PopulationId.HISTORICAL_2017_RAW_PARSE,
        archive_sha256="a"*64,
        parser_spec_sha256="b"*64,
        rows=10,
        columns=5
    )
    df = pd.DataFrame({"a": [1, 2, 3]})
    frame = PopulationFrame(df=df, ref=ref)

    assert frame.df is df
    assert frame.ref is ref

    frame.df["b"] = [4, 5, 6]
    assert "b" in frame.df.columns


def test_t_foundation_run_01_run_context_identity():
    """T-FOUNDATION-RUN-01: RunContext exposes architecture-defined provenance identity."""
    from off_quality.domain import RunContext

    assert dataclasses.is_dataclass(RunContext)

    fields = {f.name: f for f in dataclasses.fields(RunContext)}

    expected_identity = {
        "run_id",
        "code_commit",
        "dataset_sha256",
        "freeze_manifest_sha256",
        "population",
        "experiment_id",
        "seeds"
    }
    for field_name in expected_identity:
        assert field_name in fields


def test_t_foundation_run_02_run_context_dirty_immutable():
    """T-FOUNDATION-RUN-02: RunContext records dirty: bool state explicitly; immutable context identity cannot be rebound; no environment_digest required in AU-1."""
    from off_quality.domain import RunContext

    assert RunContext.__dataclass_params__.frozen is True

    fields = {f.name: f.type for f in dataclasses.fields(RunContext)}

    assert "dirty" in fields
    assert fields["dirty"] is bool or fields["dirty"] == 'bool'
    assert "environment_digest" not in fields

    ctx = RunContext(
        run_id="run123",
        code_commit="abcdef1234567890",
        dataset_sha256="ds256",
        freeze_manifest_sha256="fm256",
        population="HISTORICAL_2017_RAW_PARSE",
        experiment_id="exp456",
        seeds={"seed1": 42},
        dirty=True
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.run_id = "run456"
