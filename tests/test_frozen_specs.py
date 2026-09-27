import dataclasses
import hashlib
import json
import shutil
from pathlib import Path

import pytest

EXPECTED_TRUST_ROOT_SHA256 = (
    "b0324ef21c6d1e9692e6c168d6557ff7c56fbc14d5c04a65b3be784019de67ef"
)
EXPECTED_MANIFEST_VERSION = "1.0.2"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "specs"
EXPECTED_FIELDS = {
    "compute_envelope",
    "evaluation_protocol",
    "experiment_register",
    "feature_lineage",
    "governance",
    "slice_support",
    "tolerance_register",
    "freeze_manifest",
}


def test_t_foundation_trust_01_off_quality_config_frozen_specs():
    """T-FOUNDATION-TRUST-01: config exposes a frozen typed boundary."""
    from off_quality.config import FrozenSpecs

    assert dataclasses.is_dataclass(FrozenSpecs)
    assert FrozenSpecs.__dataclass_params__.frozen is True


def test_t_foundation_trust_02_frozen_specs_payload():
    """T-FOUNDATION-TRUST-02: exactly seven payloads plus the manifest."""
    from off_quality.config import FrozenSpecs

    field_names = {field.name for field in dataclasses.fields(FrozenSpecs)}
    assert field_names == EXPECTED_FIELDS
    assert len(field_names) == 8


def test_t_foundation_trust_03_manifest_digest(tmp_path: Path):
    """T-FOUNDATION-TRUST-03: external manifest trust is fail-closed."""
    from off_quality.config import load_trusted_specs

    bundle = tmp_path / "bundle"
    shutil.copytree(FIXTURES_DIR / "valid_bundle", bundle)

    with pytest.raises(ValueError, match="(?i)manifest|digest|sha"):
        load_trusted_specs(
            bundle_path=bundle,
            expected_manifest_digest="a" * 64,
        )


def test_t_foundation_trust_04_manifest_version(tmp_path: Path):
    """T-FOUNDATION-TRUST-04: manifest version 1.0.2 is required."""
    from off_quality.config import load_trusted_specs

    bundle = tmp_path / "wrong-version"
    shutil.copytree(FIXTURES_DIR / "valid_bundle", bundle)
    manifest_path = bundle / "freeze_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = "1.0.1"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    expected_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()


    with pytest.raises(ValueError, match=r"1\.0\.2|version"):
        load_trusted_specs(
            bundle_path=bundle,
            expected_manifest_digest=expected_digest,
        )


def test_t_foundation_trust_05_bundle_replacement():
    """T-FOUNDATION-TRUST-05: a replacement bundle cannot authenticate itself."""
    from off_quality.config import load_trusted_specs

    with pytest.raises(ValueError):
        load_trusted_specs(bundle_path=FIXTURES_DIR / "substituted_bundle")


def test_t_foundation_trust_06_packaged_trust_root():
    """T-FOUNDATION-TRUST-06: packaged trust is independent of bundle data."""
    from off_quality import config

    assert config.EXPECTED_TRUST_ROOT_DIGEST == EXPECTED_TRUST_ROOT_SHA256
    substituted_manifest = (
        FIXTURES_DIR / "substituted_bundle" / "freeze_manifest.json"
    ).read_bytes()
    substituted_digest = hashlib.sha256(substituted_manifest).hexdigest()
    assert substituted_digest != config.EXPECTED_TRUST_ROOT_DIGEST


def test_t_foundation_root_01_sole_composition_root():
    """T-FOUNDATION-ROOT-01: pipeline.py remains the composition root."""
    from off_quality import pipeline

    assert callable(pipeline.verify_config)


def test_t_foundation_root_02_config_not_composition_root():
    """T-FOUNDATION-ROOT-02: config.py is a loader, not another root."""
    from off_quality import config

    assert not hasattr(config, "QualityPipeline")
    assert not hasattr(config, "build_pipeline")
    assert not hasattr(config, "verify_config")
