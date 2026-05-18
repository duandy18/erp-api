import ast
from pathlib import Path


def test_alembic_revision_ids_fit_version_table() -> None:
    for path in Path("alembic/versions").glob("*.py"):
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in module.body:
            if isinstance(node, ast.AnnAssign):
                target = node.target
                if (
                    isinstance(target, ast.Name)
                    and target.id == "revision"
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    assert len(node.value.value) <= 32, f"{path}: revision id too long"
