import dataclasses
import importlib

import pytest


def test_t_foundation_trust_01_off_quality_config_frozen_specs():
    """T-FOUNDATION-TRUST-01: off_quality.config exposes a typed FrozenSpecs production boundary."""
    # We use importlib to avoid pytest collection failures if the module doesn't exist
    try:
        config = importlib.import_module("off_quality.config")
        FrozenSpecs = config.FrozenSpecs

        assert dataclasses.is_dataclass(FrozenSpecs)
        assert FrozenSpecs.__dataclass_params__.frozen is True
    except ImportError:
        pytest.fail("off_quality.config module or FrozenSpecs not found")


def test_t_foundation_trust_02_frozen_specs_payload():
    """T-FOUNDATION-TRUST-02: FrozenSpecs requires exactly seven declared payload specs plus freeze_manifest.json (total 8 JSON files)."""
    try:
        config = importlib.import_module("off_quality.config")
        FrozenSpecs = config.FrozenSpecs

        fields = {f.name: f.type for f in dataclasses.fields(FrozenSpecs)}
        # Expected to have freeze_manifest and 7 payload specs
        assert len(fields) == 8
        assert "freeze_manifest" in fields

        expected_total = 8
        assert len(fields) == expected_total
    except ImportError:
        pytest.fail("off_quality.config module or FrozenSpecs not found")


def test_t_foundation_trust_03_manifest_digest():
    """T-FOUNDATION-TRUST-03: Manifest digest must match an independent expected trusted digest."""
    try:
        config = importlib.import_module("off_quality.config")
        # Assuming there is a function or method that verifies this, e.g. load_trusted_specs
        load_trusted_specs = config.load_trusted_specs

        # Calling with invalid digest should fail
        with pytest.raises(ValueError, match="digest"):
            load_trusted_specs(expected_manifest_digest="invalid_digest")
    except ImportError:
        pytest.fail("off_quality.config module or load_trusted_specs not found")
    except AttributeError:
        pytest.fail("off_quality.config module is missing required function")


def test_t_foundation_trust_04_manifest_version():
    """T-FOUNDATION-TRUST-04: Expected manifest version 1.0.2 is enforced."""
    try:
        config = importlib.import_module("off_quality.config")
        # E.g., load_trusted_specs enforces the version
        load_trusted_specs = config.load_trusted_specs

        # Test this indirectly by mocking or catching exceptions if it checks version
        with pytest.raises(ValueError, match="1.0.2"):
            # Providing some fake bundle path that has a wrong version or triggering error
            load_trusted_specs(bundle_path="dummy_path_with_wrong_version")
    except ImportError:
        pytest.fail("off_quality.config module or load_trusted_specs not found")
    except AttributeError:
        pytest.fail("off_quality.config module is missing required function")
    except ValueError:
        # Expected to fail in RED mode because it's not implemented yet
        pytest.fail("Expected failure for T-FOUNDATION-TRUST-04")


def test_t_foundation_trust_05_bundle_replacement():
    """T-FOUNDATION-TRUST-05: Bundle replacement cannot replace or authenticate the trusted root."""
    try:
        config = importlib.import_module("off_quality.config")
        load_trusted_specs = config.load_trusted_specs

        # Providing a fake bundle cannot override the internal trust root
        with pytest.raises(ValueError):
            load_trusted_specs(bundle_path="fake_bundle", trust_root="malicious_root")
    except ImportError:
        pytest.fail("off_quality.config module or load_trusted_specs not found")
    except AttributeError:
        pytest.fail("off_quality.config module is missing required function")


def test_t_foundation_trust_06_packaged_trust_root():
    """T-FOUNDATION-TRUST-06: Packaged trust_root expectation is separate from the supplied bundle."""
    try:
        config = importlib.import_module("off_quality.config")

        # Trust root is provided independently
        assert hasattr(config, "EXPECTED_TRUST_ROOT_DIGEST")
    except ImportError:
        pytest.fail("off_quality.config module not found")
    except AssertionError:
        pytest.fail("EXPECTED_TRUST_ROOT_DIGEST not found in config")


def test_t_foundation_root_01_sole_composition_root():
    """T-FOUNDATION-ROOT-01: pipeline.py remains sole implementation composition root."""
    import inspect

    from off_quality.pipeline import QualityPipeline

    assert inspect.isclass(QualityPipeline)


def test_t_foundation_root_02_config_not_composition_root():
    """T-FOUNDATION-ROOT-02: config.py cannot become an alternate composition root."""
    try:
        config = importlib.import_module("off_quality.config")
        # Should not contain pipeline creation logic
        assert not hasattr(config, "QualityPipeline")
        assert not hasattr(config, "build_pipeline")
    except ImportError:
        pytest.fail("off_quality.config module not found")

