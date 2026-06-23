import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tools.render_mermaid_diagrams as renderer


class RenderMermaidDiagramsTests(unittest.TestCase):
    def test_extract_diagrams_uses_nearest_h2_title_for_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "diagrams.md"
            source.write_text(
                "\n".join(
                    [
                        "# Diagrams",
                        "",
                        "## Refactor Method",
                        "",
                        "```mermaid",
                        "flowchart TD",
                        '  A["Start"] --> B["Finish"]',
                        "```",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            diagrams = renderer._extract_diagrams(source)

            self.assertEqual(len(diagrams), 1)
            self.assertEqual(diagrams[0].title, "Refactor Method")
            self.assertEqual(diagrams[0].slug, "refactor-method")
            self.assertEqual(
                diagrams[0].source,
                'flowchart TD\n  A["Start"] --> B["Finish"]\n',
            )

    def test_render_skips_unchanged_existing_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "diagrams.md"
            output_dir = tmp_path / "out"
            manifest = tmp_path / "manifest.json"
            mmdc = tmp_path / "mmdc"
            config = tmp_path / "config.json"
            diagram_source = "flowchart TD\n  A --> B\n"
            source.write_text(
                f"## Stable Diagram\n\n```mermaid\n{diagram_source}```\n",
                encoding="utf-8",
            )
            output_dir.mkdir()
            (output_dir / "stable-diagram.svg").write_text(
                "<svg />\n", encoding="utf-8"
            )
            manifest.write_text(
                json.dumps({"stable-diagram": renderer._source_hash(diagram_source)}),
                encoding="utf-8",
            )
            mmdc.write_text("#!/usr/bin/env sh\n", encoding="utf-8")
            config.write_text("{}", encoding="utf-8")

            with (
                mock.patch.object(renderer, "MMDC", mmdc),
                mock.patch.object(renderer, "MERMAID_CONFIG", config),
                mock.patch.object(renderer.subprocess, "run") as run,
            ):
                result = renderer.render_mermaid_diagrams(
                    source,
                    output_dir,
                    manifest,
                )

            run.assert_not_called()
            self.assertEqual(result.updated_paths, [])
            self.assertEqual(result.skipped_paths, [output_dir / "stable-diagram.svg"])

    def test_render_writes_svg_and_manifest_when_source_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "diagrams.md"
            output_dir = tmp_path / "out"
            manifest = tmp_path / "manifest.json"
            mmdc = tmp_path / "mmdc"
            config = tmp_path / "config.json"
            source.write_text(
                "## Fresh Diagram\n\n```mermaid\nflowchart LR\n  A --> B\n```\n",
                encoding="utf-8",
            )
            mmdc.write_text("#!/usr/bin/env sh\n", encoding="utf-8")
            config.write_text("{}", encoding="utf-8")

            def fake_run(args: list[str], *, check: bool) -> None:
                self.assertTrue(check)
                Path(args[-1]).write_text("<svg>fresh</svg>\n", encoding="utf-8")

            with (
                mock.patch.object(renderer, "MMDC", mmdc),
                mock.patch.object(renderer, "MERMAID_CONFIG", config),
                mock.patch.object(renderer.subprocess, "run", side_effect=fake_run),
            ):
                result = renderer.render_mermaid_diagrams(
                    source,
                    output_dir,
                    manifest,
                )

            output = output_dir / "fresh-diagram.svg"
            self.assertEqual(output.read_text(encoding="utf-8"), "<svg>fresh</svg>\n")
            self.assertEqual(result.updated_paths, [output])
            self.assertEqual(result.skipped_paths, [])
            self.assertIn("fresh-diagram", json.loads(manifest.read_text()))

    def test_render_rejects_duplicate_diagram_slugs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "diagrams.md"
            mmdc = tmp_path / "mmdc"
            config = tmp_path / "config.json"
            source.write_text(
                "\n".join(
                    [
                        "## Same Title",
                        "```mermaid",
                        "flowchart TD",
                        "  A --> B",
                        "```",
                        "## Same Title!",
                        "```mermaid",
                        "flowchart TD",
                        "  C --> D",
                        "```",
                    ]
                ),
                encoding="utf-8",
            )
            mmdc.write_text("#!/usr/bin/env sh\n", encoding="utf-8")
            config.write_text("{}", encoding="utf-8")

            with (
                mock.patch.object(renderer, "MMDC", mmdc),
                mock.patch.object(renderer, "MERMAID_CONFIG", config),
                self.assertRaisesRegex(RuntimeError, "Duplicate Mermaid diagram slugs"),
            ):
                renderer.render_mermaid_diagrams(
                    source,
                    tmp_path / "out",
                    tmp_path / "manifest.json",
                )
