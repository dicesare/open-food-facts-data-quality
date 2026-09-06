import ast
import inspect
from collections.abc import Callable
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import get_type_hints

import pandas as pd
import pytest

import off_quality
from off_quality import (
    ColumnImputer,
    DataProfiler,
    FittedColumnImputer,
    ImputationMethod,
    QualityPipeline,
    clean_products,
    missingness,
)
from off_quality.domain import (
    CleaningReport,
    LegacyEvidenceStatus,
    LegacyEvidenceTransitionError,
    LegacyUnprovenancedWarning,
    _warn_legacy_entry_point,
)
from off_quality.profiling import DatasetProfile

PACKAGE_ROOT = Path(__file__).parents[1] / "src" / "off_quality"
LEGACY_MODULES = {
    "off_quality.cleaning",
    "off_quality.imputation",
    "off_quality.pipeline",
    "off_quality.profiling",
}
LEGACY_SYMBOLS = {
    "clean_products",
    "missingness",
    "QualityPipeline",
    "DataProfiler",
    "ColumnImputer",
    "FittedColumnImputer",
}
CLI_PIPELINE_DELEGATES = {"verify_config"}
ALLOWED_BOUNDARY_FILES = {
    "__init__.py",
    "cleaning.py",
    "domain.py",
    "imputation.py",
    "pipeline.py",
    "profiling.py",
}


def _legacy_calls() -> list[tuple[str, Callable[[], object]]]:
    frame = pd.DataFrame({"code": [" 12345678 "], "value": [None]})
    fitted = FittedColumnImputer({"value": 0})
    return [
        ("clean_products", lambda: clean_products(frame)),
        ("missingness", lambda: missingness(frame)),
        ("QualityPipeline.run", lambda: QualityPipeline().run(frame)),
        (
            "QualityPipeline.run_stream",
            lambda: list(QualityPipeline().run_stream([frame])),
        ),
        ("DataProfiler.profile", lambda: DataProfiler().profile(frame)),
        (
            "ColumnImputer.fit",
            lambda: ColumnImputer(("value",), ImputationMethod.CONSTANT, 0).fit(frame),
        ),
        ("FittedColumnImputer.transform", lambda: fitted.transform(frame)),
    ]


@pytest.mark.parametrize(("entry_point", "call"), _legacy_calls())
def test_t_leg_01_each_raw_frame_entry_point_warns_once_at_the_caller(
    entry_point: str, call: Callable[[], object]
) -> None:
    with pytest.warns(LegacyUnprovenancedWarning) as caught:
        call()

    assert len(caught) == 1
    warning = caught[0]
    assert entry_point in str(warning.message)
    assert "LEGACY_UNPROVENANCED" in str(warning.message)
    assert warning.filename == __file__
    assert isinstance(warning.message, LegacyUnprovenancedWarning)
    assert warning.message.evidence_status is LegacyEvidenceStatus.LEGACY_UNPROVENANCED


def test_t_leg_02_public_signatures_exports_and_results_remain_compatible() -> None:
    assert len(off_quality.__all__) == 14
    assert "LegacyEvidenceStatus" not in off_quality.__all__
    assert tuple(inspect.signature(clean_products).parameters) == (
        "data",
        "max_missing",
    )
    assert inspect.signature(clean_products).parameters["max_missing"].default == 0.6
    assert tuple(inspect.signature(missingness).parameters) == ("data",)
    assert tuple(inspect.signature(QualityPipeline.run).parameters) == ("self", "frame")
    assert tuple(inspect.signature(DataProfiler.profile).parameters) == (
        "self",
        "frame",
        "key",
    )
    assert inspect.signature(DataProfiler.profile).parameters["key"].default == "code"
    assert tuple(inspect.signature(ColumnImputer.fit).parameters) == ("self", "frame")
    assert tuple(inspect.signature(FittedColumnImputer.transform).parameters) == (
        "self",
        "frame",
    )
    assert (
        get_type_hints(clean_products)["return"] == tuple[pd.DataFrame, CleaningReport]
    )
    assert get_type_hints(missingness)["return"] is pd.Series
    assert get_type_hints(DataProfiler.profile)["return"] is DatasetProfile

    frame = pd.DataFrame(
        {
            " code ": [" 12345678 ", "12345678", "bad"],
            "keep-at-limit": [1.0, None, 3.0],
            "drop-above-limit": [1.0, None, None],
        }
    )
    original = frame.copy(deep=True)
    with pytest.warns(LegacyUnprovenancedWarning):
        cleaned, report = clean_products(frame, max_missing=1 / 3)

    assert cleaned.to_dict(orient="records") == [
        {"code": "12345678", "keep_at_limit": 1.0}
    ]
    assert report.input_rows == 3
    assert report.output_rows == 1
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("forbidden", ["REPRODUCED", *[f"E{i}" for i in range(9)]])
def test_t_leg_03_legacy_classification_cannot_transition_to_evidence(
    forbidden: str,
) -> None:
    with pytest.raises(LegacyEvidenceTransitionError, match="LEGACY_UNPROVENANCED"):
        _warn_legacy_entry_point("test", requested_status=forbidden)  # type: ignore[arg-type]


def test_t_leg_03_status_and_warning_classification_are_immutable() -> None:
    status = LegacyEvidenceStatus.LEGACY_UNPROVENANCED
    assert tuple(LegacyEvidenceStatus) == (status,)
    with pytest.raises(AttributeError):
        status.value = "REPRODUCED"  # type: ignore[misc]

    warning = LegacyUnprovenancedWarning("legacy")
    assert warning.evidence_status is status
    with pytest.raises((AttributeError, FrozenInstanceError)):
        warning.evidence_status = LegacyEvidenceStatus.LEGACY_UNPROVENANCED  # type: ignore[misc]


def _absolute_import(module: str, level: int, current_module: str) -> str:
    if level == 0:
        return module
    package_parts = current_module.split(".")[:-1]
    keep = len(package_parts) - (level - 1)
    base = package_parts[:keep]
    return ".".join([*base, *module.split(".")]) if module else ".".join(base)


def _legacy_import_violations(
    source: str, current_module: str
) -> list[tuple[int, str]]:
    tree = ast.parse(source)
    violations: list[tuple[int, str]] = []
    importlib_modules = {"importlib"}
    import_module_functions = {"import_module"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "importlib":
                    importlib_modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "importlib":
            for alias in node.names:
                if alias.name == "import_module":
                    import_module_functions.add(alias.asname or alias.name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in LEGACY_MODULES:
                    violations.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            imported_module = _absolute_import(
                node.module or "", node.level, current_module
            )
            for alias in node.names:
                target = (
                    f"{imported_module}.{alias.name}" if imported_module else alias.name
                )
                cli_root_import = (
                    current_module == "off_quality.cli"
                    and imported_module == "off_quality.pipeline"
                    and alias.name in CLI_PIPELINE_DELEGATES
                )
                if (
                    (imported_module in LEGACY_MODULES and not cli_root_import)
                    or (
                        imported_module == "off_quality"
                        and alias.name in LEGACY_SYMBOLS
                    )
                    or target in LEGACY_MODULES
                ):
                    violations.append((node.lineno, target))
        elif isinstance(node, ast.Call) and node.args:
            function = node.func
            is_import_module = (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id in importlib_modules
                and function.attr == "import_module"
            )
            is_named_import = isinstance(function, ast.Name) and function.id in {
                *import_module_functions,
                "__import__",
            }
            first_arg = node.args[0]
            if (is_import_module or is_named_import) and isinstance(
                first_arg, ast.Constant
            ):
                literal_target = first_arg.value
                if isinstance(literal_target, str) and literal_target in LEGACY_MODULES:
                    violations.append((node.lineno, literal_target))
    return violations


def _tree_legacy_import_violations(package_root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(package_root.rglob("*.py")):
        if path.parent == package_root and path.name in ALLOWED_BOUNDARY_FILES:
            continue
        relative = path.relative_to(package_root).with_suffix("")
        current_module = ".".join(("off_quality", *relative.parts))
        for lineno, target in _legacy_import_violations(
            path.read_text(encoding="utf-8"), current_module
        ):
            violations.append(f"{path.relative_to(package_root)}:{lineno}: {target}")

    return violations


def test_t_leg_04_new_namespace_does_not_import_legacy_implementation() -> None:
    assert _tree_legacy_import_violations(PACKAGE_ROOT) == []


def test_t_leg_04_tree_scan_is_not_vacuous_for_future_modules(tmp_path: Path) -> None:
    package = tmp_path / "off_quality"
    package.mkdir()
    (package / "config.py").write_text(
        "from off_quality import clean_products\n", encoding="utf-8"
    )
    assert _tree_legacy_import_violations(package) == [
        "config.py:1: off_quality.clean_products"
    ]


@pytest.mark.parametrize(
    ("source", "module", "target"),
    [
        (
            "import off_quality.pipeline as legacy",
            "off_quality.evidence",
            "off_quality.pipeline",
        ),
        (
            "from off_quality import clean_products as clean",
            "off_quality.evidence",
            "off_quality.clean_products",
        ),
        (
            "from .pipeline import QualityPipeline",
            "off_quality.evidence",
            "off_quality.pipeline.QualityPipeline",
        ),
        ("from . import profiling", "off_quality.evidence", "off_quality.profiling"),
        (
            "import importlib\nimportlib.import_module('off_quality.imputation')",
            "off_quality.evidence",
            "off_quality.imputation",
        ),
        (
            "__import__('off_quality.cleaning')",
            "off_quality.evidence",
            "off_quality.cleaning",
        ),
        (
            "from importlib import import_module as load\nload('off_quality.pipeline')",
            "off_quality.evidence",
            "off_quality.pipeline",
        ),
        (
            "import importlib as il\nil.import_module('off_quality.profiling')",
            "off_quality.evidence",
            "off_quality.profiling",
        ),
    ],
)
def test_t_leg_04_ast_barrier_detects_real_import_forms(
    source: str, module: str, target: str
) -> None:
    assert target in {
        violation for _, violation in _legacy_import_violations(source, module)
    }


def test_t_leg_04_ast_barrier_allows_domain_types() -> None:
    source = "from .domain import CleaningReport, LegacyEvidenceStatus"
    assert _legacy_import_violations(source, "off_quality.evidence") == []


def test_t_leg_04_cli_may_delegate_only_to_non_raw_pipeline_symbols() -> None:
    allowed = "from .pipeline import verify_config"
    forbidden = "from .pipeline import QualityPipeline"
    assert _legacy_import_violations(allowed, "off_quality.cli") == []
    assert _legacy_import_violations(forbidden, "off_quality.cli") == [
        (1, "off_quality.pipeline.QualityPipeline")
    ]


@pytest.mark.parametrize(
    "source",
    [
        "import off_quality.pipeline as root\nroot.QualityPipeline()",
        (
            "from importlib import import_module as load\n"
            "root = load('off_quality.pipeline')\nroot.QualityPipeline()"
        ),
        "from .pipeline import NormalizeColumns",
    ],
)
def test_t_leg_04_cli_cannot_bypass_named_delegation(source: str) -> None:
    assert _legacy_import_violations(source, "off_quality.cli")
