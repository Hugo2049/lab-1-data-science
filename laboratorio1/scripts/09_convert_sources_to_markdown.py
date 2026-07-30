#!/usr/bin/env python3
"""Convierte notebooks .ipynb y archivos .pdf a Markdown con la salida ejecutada.

Ejemplo:
    python laboratorio1/scripts/09_convert_sources_to_markdown.py --input laboratorio2/info
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_cell_source(source: object) -> str:
    if isinstance(source, list):
        return "".join(str(item) for item in source)
    return str(source or "")


def _flatten_text_payload(payload: object) -> str:
    if isinstance(payload, list):
        return "".join(str(item) for item in payload)
    return str(payload or "")


def _format_output(output: dict) -> list[str]:
    lines: list[str] = []
    output_type = output.get("output_type")

    if output_type == "stream":
        stream_text = _flatten_text_payload(output.get("text", []))
        if stream_text:
            lines.append(stream_text.rstrip())
    elif output_type == "error":
        error_text = "\n".join(part for part in [output.get("ename", ""), output.get("evalue", "")] if part)
        if error_text:
            lines.append("```text")
            lines.append(error_text)
            lines.append("```")
        if output.get("traceback"):
            lines.append("```text")
            lines.extend(str(item) for item in output.get("traceback", []))
            lines.append("```")
    elif output_type in {"execute_result", "display_data"}:
        data = output.get("data", {})
        text_parts: list[str] = []
        if "text/plain" in data:
            text_parts.append(_flatten_text_payload(data.get("text/plain", [])))
        if "text/html" in data:
            text_parts.append("```html")
            text_parts.append(_flatten_text_payload(data.get("text/html", [])))
            text_parts.append("```")
        if "image/png" in data:
            image_b64 = data.get("image/png", "")
            image_uri = f"data:image/png;base64,{image_b64}"
            text_parts.append(f"![Notebook output]({image_uri})")
        if "application/vnd.plotly.v1+json" in data:
            text_parts.append("```json")
            text_parts.append(json.dumps(data.get("application/vnd.plotly.v1+json"), indent=2, ensure_ascii=False))
            text_parts.append("```")
        lines.extend(part for part in text_parts if part)

    return lines


def notebook_to_markdown(notebook_path: Path) -> str:
    notebook = json.loads(_read_text(notebook_path))
    cell_sections: list[str] = []
    cell_sections.append(f"# {notebook_path.stem}\n")

    for index, cell in enumerate(notebook.get("cells", []), start=1):
        cell_type = cell.get("cell_type", "code")
        if cell_type == "markdown":
            cell_sections.append(f"## Cell {index} (markdown)\n")
            cell_sections.append(_normalize_cell_source(cell.get("source", [])))
            cell_sections.append("\n")
        elif cell_type == "code":
            cell_sections.append(f"## Cell {index} (code)\n")
            cell_sections.append("```python")
            cell_sections.append(_normalize_cell_source(cell.get("source", [])).rstrip())
            cell_sections.append("```\n")
            outputs: list[dict] = cell.get("outputs", [])
            if outputs:
                cell_sections.append("### Outputs\n")
                for output in outputs:
                    rendered_lines = _format_output(output)
                    if rendered_lines:
                        cell_sections.extend(rendered_lines)
                        cell_sections.append("\n")

    return "\n".join(part for part in cell_sections if part is not None).strip() + "\n"


def pdf_to_markdown(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                pages.append(page_text.strip())
        text = "\n\n".join(pages).strip()
        if not text:
            raise ValueError("No text could be extracted from the PDF")
        return f"# {pdf_path.stem}\n\n{text}\n"
    except Exception as exc:
        try:
            result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            text = result.stdout.strip()
            if not text:
                raise ValueError("pdftotext returned no text")
            return f"# {pdf_path.stem}\n\n{text}\n"
        except Exception:
            raise RuntimeError(
                f"No se pudo extraer texto del PDF '{pdf_path.name}'. Instala 'pypdf' o 'pdftotext'."
            ) from exc


def convert_notebook(notebook_path: Path, output_dir: Path) -> Path:
    output_path = output_dir / f"{notebook_path.stem}.md"
    output_path.write_text(notebook_to_markdown(notebook_path), encoding="utf-8")
    return output_path


def convert_pdf(pdf_path: Path, output_dir: Path) -> Path:
    output_path = output_dir / f"{pdf_path.stem}.md"
    output_path.write_text(pdf_to_markdown(pdf_path), encoding="utf-8")
    return output_path


def iter_supported_files(target_dir: Path) -> Iterable[Path]:
    return sorted(
        p
        for p in target_dir.rglob("*")
        if p.is_file() and (p.suffix.lower() in {".ipynb", ".pdf"})
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Convierte notebooks y PDFs en Markdown representando todo el contenido ejecutado.")
    parser.add_argument("--input", default="laboratorio2/info", help="Directorio con archivos .ipynb y .pdf")
    parser.add_argument("--output", default=None, help="Directorio de destino para .md (por defecto: mismo directorio)")
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        raise SystemExit(f"El directorio de entrada no existe: {input_dir}")

    output_dir = Path(args.output) if args.output else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = []
    for file_path in iter_supported_files(input_dir):
        if file_path.suffix.lower() == ".ipynb":
            converted.append(convert_notebook(file_path, output_dir))
        else:
            converted.append(convert_pdf(file_path, output_dir))

    print(f"Archivos convertidos: {len(converted)}")
    for path in converted:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
