import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1] / "src" / "off_quality"

EXPECTED_INTERNAL_IMPORTS = {
    "__init__": {"cleaning", "domain", "imputation", "pipeline", "profiling"},
    "cleaning": {"domain", "pipeline"},
    "cli": {"pipeline"},
    "domain": set(),
    "imputation": {"domain"},
    "pipeline": {"domain"},
    "profiling": {"domain"},
}


def _internal_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            imports.add(node.module.split(".", maxsplit=1)[0])
    return imports


def test_internal_import_graph_is_characterized() -> None:
    observed = {
        path.stem: _internal_imports(path)
        for path in sorted(PACKAGE_ROOT.glob("*.py"))
    }

    assert observed == EXPECTED_INTERNAL_IMPORTS


def test_pipeline_is_the_only_current_composition_module() -> None:
    implementation_modules = {
        path.stem for path in PACKAGE_ROOT.glob("*.py") if path.stem != "__init__"
    }

    assert "pipeline" in implementation_modules
    assert "pipelines" not in implementation_modules
