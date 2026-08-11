import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bilingual_readmes_link_project_evidence() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    english = (ROOT / "README.en.md").read_text(encoding="utf-8")
    for term in (
        "docs/project_story.md",
        "docs/contribution_matrix.md",
        "docs/evidence_index.md",
        "docs/manuals/README.md",
    ):
        assert term in readme
        assert term in english
    assert "README.en.md" in readme


def test_all_new_markdown_links_resolve() -> None:
    documents = [ROOT / "README.en.md", *(ROOT / "docs").rglob("*.md")]
    pattern = re.compile(r"\[[^]]*]\(([^)]+)\)")
    broken: list[str] = []
    for document in documents:
        for raw in pattern.findall(document.read_text(encoding="utf-8")):
            target = raw.split("#", maxsplit=1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (document.parent / target).resolve().exists():
                broken.append(f"{document.relative_to(ROOT)} -> {raw}")
    assert not broken, "broken links: " + ", ".join(broken)


def test_manual_inventory_has_nine_pdfs() -> None:
    assert len(list((ROOT / "docs/manuals").glob("*.pdf"))) == 9
