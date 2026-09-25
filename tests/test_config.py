import importlib
import subprocess
import sys
from pathlib import Path

EXPECTED_SHA256 = "b0324ef21c6d1e9692e6c168d6557ff7c56fbc14d5c04a65b3be784019de67ef"
EXPECTED_VERSION = "1.0.2"
SCHEMA_FAILURE_EXPECTED_SHA256 = (
    "b487de4e88eb41fec22d0669e3eb05620d4c26926c21697f1a6aafae124cffb5"
)
CROSS_REF_FAILURE_EXPECTED_SHA256 = (
    "5646a70f7ba05530eb3686240a24fb81cc39f42c55becc4586c4fce71eb8af3e"
)
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "specs"


def test_t_trust_01_whole_bundle_substitution_rejected():
    """T-TRUST-01: Whole-bundle substitution is rejected.

    A supplied spec bundle must not be able to authenticate itself.
    Replacing the bundle while retaining the externally trusted expected
    manifest digest must fail closed.
    """
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "substituted_bundle"
    # Even if substituted_bundle is internally coherent, it must not match the trusted anchor
    result = pipeline.verify_config(bundle_path, EXPECTED_SHA256)
    assert result is False, "Verification must fail when bundle tries to authenticate itself"


def test_t_trust_02_wrong_external_digest_rejected():
    """T-TRUST-02: Wrong external digest is rejected.

    If the expected external freeze_manifest SHA-256 differs from the actual
    reviewed manifest digest, verification must fail closed.
    """
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "valid_bundle"
    wrong_sha256 = "a" * 64

    result = pipeline.verify_config(bundle_path, wrong_sha256)
    assert result is False, "Verification must fail when expected external digest differs"


def test_t_trust_03_arbitrary_or_unknown_roots_rejected():
    """T-TRUST-03: Arbitrary or unknown roots are rejected.

    Normal production verification must not silently trust an arbitrary spec root.
    """
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "unknown_root"

    result = pipeline.verify_config(bundle_path, EXPECTED_SHA256)
    assert result is False, "Verification must fail closed for arbitrary or unknown roots"


def test_t_trust_04_missing_file_rejected():
    """T-TRUST-04 Scenario 1: Missing required file is rejected."""
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "missing_file"
    result = pipeline.verify_config(bundle_path, EXPECTED_SHA256)
    assert result is False, "Verification must fail when a required spec file is missing"


def test_t_trust_04_extra_file_rejected():
    """T-TRUST-04 Scenario 2: Unexpected extra file is rejected."""
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "extra_file"
    result = pipeline.verify_config(bundle_path, EXPECTED_SHA256)
    assert result is False, "Verification must fail when an unlisted extra file is present"


def test_t_trust_04_digest_mismatch_rejected():
    """T-TRUST-04 Scenario 3: Per-file digest mismatch is rejected."""
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "digest_mismatch"
    result = pipeline.verify_config(bundle_path, EXPECTED_SHA256)
    assert result is False, "Verification must fail when a spec file digest does not match manifest"


def test_t_trust_04_schema_failure_rejected():
    """T-TRUST-04 Scenario 4: Schema validation failure is rejected."""
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "schema_failure"

    # Must fail even when manifest digest matches because structured schema is invalid
    result = pipeline.verify_config(bundle_path, SCHEMA_FAILURE_EXPECTED_SHA256)
    assert result is False, "Verification must fail when structured schema validation fails"


def test_t_trust_04_cross_ref_failure_rejected():
    """T-TRUST-04 Scenario 5: Cross-reference and semantic rule failure is rejected."""
    from off_quality import pipeline

    bundle_path = FIXTURES_DIR / "cross_ref_failure"

    # Must fail even when manifest digest matches because semantic cross-reference rules are broken
    result = pipeline.verify_config(bundle_path, CROSS_REF_FAILURE_EXPECTED_SHA256)
    assert result is False, "Verification must fail when semantic cross-references are broken"


def test_t_trust_04_bundle_integrity_failures_rejected():
    """T-TRUST-04 Summary: All five isolated integrity and semantic failure classes."""
    from off_quality import pipeline

    # 1. missing_file
    assert pipeline.verify_config(FIXTURES_DIR / "missing_file", EXPECTED_SHA256) is False
    # 2. extra_file
    assert pipeline.verify_config(FIXTURES_DIR / "extra_file", EXPECTED_SHA256) is False
    # 3. digest_mismatch
    assert pipeline.verify_config(FIXTURES_DIR / "digest_mismatch", EXPECTED_SHA256) is False
    # 4. schema_failure
    assert (
        pipeline.verify_config(
            FIXTURES_DIR / "schema_failure", SCHEMA_FAILURE_EXPECTED_SHA256
        )
        is False
    )
    # 5. cross_ref_failure
    assert (
        pipeline.verify_config(
            FIXTURES_DIR / "cross_ref_failure", CROSS_REF_FAILURE_EXPECTED_SHA256
        )
        is False
    )


def test_t_cli_01_cli_contract_help():
    """T-CLI-01: python -m off_quality.cli --help"""
    result = subprocess.run(
        [sys.executable, "-m", "off_quality.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, "CLI must successfully return help text"
    assert "verify-config" in result.stdout


def test_t_cli_01_cli_contract_verify_config():
    """T-CLI-01: python -m off_quality.cli verify-config"""
    bundle_path = FIXTURES_DIR / "valid_bundle"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "off_quality.cli",
            "verify-config",
            "--bundle",
            str(bundle_path),
            "--expected-sha256",
            EXPECTED_SHA256,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, "CLI verify-config must return 0 for a valid bundle"


def test_t_root_01_composition_root():
    """T-ROOT-01 Part A: pipeline.py is the sole implementation composition root."""
    from off_quality import pipeline

    assert hasattr(pipeline, "verify_config"), (
        "pipeline.py must be the sole composition root exposing verify_config"
    )


def test_t_root_01_cli_delegates_to_pipeline(monkeypatch):
    """T-ROOT-01 Part B: CLI verify-config delegates to pipeline.verify_config."""
    from off_quality import pipeline

    assert hasattr(pipeline, "verify_config"), (
        "pipeline.py must expose verify_config composition root"
    )

    calls = []

    def spy_verify_config(bundle_path, expected_sha256):
        calls.append((Path(bundle_path), str(expected_sha256)))
        return True

    monkeypatch.setattr(pipeline, "verify_config", spy_verify_config)

    cli_mod = importlib.import_module("off_quality.cli")
    runner = getattr(cli_mod, "main", getattr(cli_mod, "cli", None))
    assert callable(runner), "off_quality.cli must provide a callable entry point (main or cli)"

    bundle_path = FIXTURES_DIR / "valid_bundle"
    exit_code = runner(["verify-config", "--bundle", str(bundle_path), "--expected-sha256", EXPECTED_SHA256])
    assert exit_code == 0, "CLI verify-config must return exit code 0 when pipeline.verify_config succeeds"
    assert len(calls) == 1, "CLI must delegate execution directly to pipeline.verify_config"
    assert calls[0][1] == EXPECTED_SHA256, "CLI must forward the expected SHA-256 to pipeline.verify_config"
