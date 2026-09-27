import dataclasses

import pandas as pd
import pytest


def test_t_foundation_domain_01_population_id():
    """T-FOUNDATION-DOMAIN-01: architecture population IDs exist."""
    from off_quality.domain import PopulationId

    assert PopulationId.HISTORICAL_2017_RAW_PARSE == "HISTORICAL_2017_RAW_PARSE"
    assert PopulationId.HISTORICAL_2017_CORRECTED == "HISTORICAL_2017_CORRECTED"


def test_t_foundation_domain_02_population_ref():
    """T-FOUNDATION-DOMAIN-02: PopulationRef is the frozen exact value object."""
    from off_quality.domain import PopulationId, PopulationRef

    assert dataclasses.is_dataclass(PopulationRef)
    assert PopulationRef.__dataclass_params__.frozen is True
    assert {field.name for field in dataclasses.fields(PopulationRef)} == {
        "population_id",
        "archive_sha256",
        "parser_spec_sha256",
        "rows",
        "columns",
    }


    ref = PopulationRef(
        population_id=PopulationId.HISTORICAL_2017_RAW_PARSE,
        archive_sha256="a" * 64,
        parser_spec_sha256="b" * 64,
        rows=10,
        columns=5,
    )
    assert ref.rows == 10
    with pytest.raises(dataclasses.FrozenInstanceError):
        ref.rows = 20


def test_t_foundation_domain_03_population_frame():
    """T-FOUNDATION-DOMAIN-03: frame and provenance are paired without deep immutability."""
    from off_quality.domain import PopulationFrame, PopulationId, PopulationRef

    ref = PopulationRef(
        population_id=PopulationId.HISTORICAL_2017_RAW_PARSE,
        archive_sha256="a" * 64,
        parser_spec_sha256="b" * 64,
        rows=3,
        columns=1,
    )
    dataframe = pd.DataFrame({"a": [1, 2, 3]})
    population_frame = PopulationFrame(dataframe, ref)


    values = [
        getattr(population_frame, field.name)
        for field in dataclasses.fields(PopulationFrame)
    ]
    assert any(value is dataframe for value in values)
    assert any(value is ref for value in values)

    dataframe["b"] = [4, 5, 6]
    assert "b" in dataframe.columns


def test_t_foundation_run_01_run_context_identity():
    """T-FOUNDATION-RUN-01: RunContext exposes the required provenance identity."""
    from off_quality.domain import RunContext

    assert dataclasses.is_dataclass(RunContext)
    field_names = {field.name for field in dataclasses.fields(RunContext)}
    assert {
        "run_id",
        "code_commit",
        "dataset_sha256",
        "freeze_manifest_sha256",
        "population",
        "experiment_id",
        "seeds",
    } <= field_names


def test_t_foundation_run_02_run_context_dirty_immutable():
    """T-FOUNDATION-RUN-02: dirty state is explicit and context identity is frozen."""
    from off_quality.domain import RunContext

    assert RunContext.__dataclass_params__.frozen is True
    fields = {field.name: field.type for field in dataclasses.fields(RunContext)}
    assert "dirty" in fields
    assert fields["dirty"] is bool or fields["dirty"] == "bool"
    assert "environment_digest" not in fields
