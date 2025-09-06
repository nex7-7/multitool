"""
PDF processing tools implementation.
Each class follows Single Responsibility Principle - one tool, one responsibility.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import io
import logging

from flask import url_for
from PIL import Image
from pypdf import PdfReader, PdfWriter
import pdfplumber

from ...utils.base import ToolBase, ProcessingResult

logger = logging.getLogger(__name__)


def _build_output_url(output_path: Path) -> str:
    """Return the public URL for a saved output file using only basename."""
    return url_for('main.serve_output_file', filename=Path(output_path).name, _external=True)


def _parse_page_ranges(pages: Optional[str], total_pages: int) -> List[int]:
    """Parse a human-friendly page ranges string into 0-based page indices.

    Examples:
        "1-3,5,7-" -> [0,1,2,4,6,...to end]
    """
    if not pages:
        return list(range(total_pages))

    indices: List[int] = []
    for part in pages.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start_str, end_str = part.split('-', 1)
            try:
                start = int(start_str) - 1 if start_str else 0
            except ValueError:
                raise ValueError(f"Invalid page start: {start_str}")
            if end_str:
                try:
                    end = int(end_str) - 1
                except ValueError:
                    raise ValueError(f"Invalid page end: {end_str}")
            else:
                end = total_pages - 1
            if start < 0 or end < 0 or start > end:
                raise ValueError(f"Invalid range: {part}")
            indices.extend(list(range(start, min(end, total_pages - 1) + 1)))
        else:
            try:
                idx = int(part) - 1
            except ValueError:
                raise ValueError(f"Invalid page number: {part}")
            if idx < 0 or idx >= total_pages:
                raise ValueError(f"Page out of bounds: {part}")
            indices.append(idx)

    # Deduplicate while preserving order
    seen = set()
    ordered_unique = [i for i in indices if (i not in seen and not seen.add(i))]
    return ordered_unique


class PDFSplitter(ToolBase):
    """Split PDF into individual pages or a selected range."""

    def process(self, pages: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            reader = PdfReader(str(self.input_path))
            total = len(reader.pages)
            indices = _parse_page_ranges(pages, total) if pages else None

            outputs: List[Dict[str, Any]] = []
            if indices:
                writer = PdfWriter()
                for i in indices:
                    writer.add_page(reader.pages[i])

                if not self.output_path:
                    return ProcessingResult(True, "Split in memory", metadata={"pages": indices}).to_dict()

                with open(self.output_path, 'wb') as f:
                    writer.write(f)
                outputs.append({
                    'output_path': str(self.output_path),
                    'output_url': _build_output_url(Path(self.output_path)),
                    'pages': [i + 1 for i in indices]
                })
            else:
                # Split into individual pages
                if not self.output_path:
                    return ProcessingResult(True, "Split in memory", metadata={"pages": list(range(total))}).to_dict()

                base = Path(self.output_path)
                stem = base.stem
                for i in range(total):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    out_path = base.with_name(f"{stem}_page_{i+1}.pdf")
                    with open(out_path, 'wb') as f:
                        writer.write(f)
                    outputs.append({
                        'output_path': str(out_path),
                        'output_url': _build_output_url(out_path),
                        'page': i + 1
                    })

            return ProcessingResult(
                success=True,
                message="PDF split successfully",
                output_path=str(self.output_path) if self.output_path else None,
                output_url=_build_output_url(Path(self.output_path)) if self.output_path else None,
                metadata={'outputs': outputs, 'total_pages': total}
            ).to_dict()

        except Exception as e:
            logger.error(f"Error splitting PDF: {e}")
            return ProcessingResult(False, f"Failed to split PDF: {e}").to_dict()


class PDFMerger:
    """Merge multiple PDFs into one output file."""

    def __init__(self, input_paths: List[str], output_path: Optional[str] = None):
        self.input_paths = [Path(p) for p in input_paths]
        self.output_path = Path(output_path) if output_path else None

    def process(self) -> Dict[str, Any]:
        try:
            writer = PdfWriter()
            total_pages = 0
            for path in self.input_paths:
                reader = PdfReader(str(path))
                for page in reader.pages:
                    writer.add_page(page)
                total_pages += len(reader.pages)

            if not self.output_path:
                return ProcessingResult(True, "Merged in memory", metadata={'files': [p.name for p in self.input_paths]}).to_dict()

            with open(self.output_path, 'wb') as f:
                writer.write(f)

            return ProcessingResult(
                True,
                "PDFs merged successfully",
                output_path=str(self.output_path),
                output_url=_build_output_url(Path(self.output_path)),
                metadata={'files': [str(p) for p in self.input_paths], 'total_pages': total_pages}
            ).to_dict()

        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            return ProcessingResult(False, f"Failed to merge PDFs: {e}").to_dict()


class PDFRearranger(ToolBase):
    """Reorder pages of a PDF according to a given sequence (1-based indices)."""

    def process(self, page_order: List[int], **kwargs) -> Dict[str, Any]:
        try:
            reader = PdfReader(str(self.input_path))
            total = len(reader.pages)

            if not page_order:
                return ProcessingResult(False, "page_order is required").to_dict()

            # Validate order
            zero_based = [p - 1 for p in page_order]
            if any(p < 0 or p >= total for p in zero_based):
                return ProcessingResult(False, "page_order contains out-of-bounds indices").to_dict()
            if sorted(zero_based) != list(range(total)):
                return ProcessingResult(False, "page_order must be a permutation of all pages").to_dict()

            writer = PdfWriter()
            for idx in zero_based:
                writer.add_page(reader.pages[idx])

            if not self.output_path:
                return ProcessingResult(True, "Reordered in memory", metadata={'page_order': page_order}).to_dict()

            with open(self.output_path, 'wb') as f:
                writer.write(f)

            return ProcessingResult(
                True,
                "PDF pages rearranged successfully",
                output_path=str(self.output_path),
                output_url=_build_output_url(Path(self.output_path)),
                metadata={'page_order': page_order, 'total_pages': total}
            ).to_dict()

        except Exception as e:
            logger.error(f"Error rearranging PDF: {e}")
            return ProcessingResult(False, f"Failed to rearrange PDF: {e}").to_dict()


class ConvertToPDF(ToolBase):
    """Convert supported files (e.g., images) to PDF."""

    SUPPORTED_IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}

    def process(self, **kwargs) -> Dict[str, Any]:
        try:
            ext = self.input_path.suffix.lower()
            if ext == '.pdf':
                # If already a PDF, copy to output
                if not self.output_path:
                    return ProcessingResult(True, "Already a PDF; no output path provided", metadata={}).to_dict()
                # Simple byte copy
                data = Path(self.input_path).read_bytes()
                Path(self.output_path).write_bytes(data)
                return ProcessingResult(
                    True,
                    "File was already PDF; copied",
                    output_path=str(self.output_path),
                    output_url=_build_output_url(Path(self.output_path)),
                ).to_dict()

            if ext not in self.SUPPORTED_IMAGE_EXTS:
                return ProcessingResult(False, f"Unsupported input format for PDF conversion: {ext}").to_dict()

            if not self.output_path:
                return ProcessingResult(False, "Output path is required for conversion").to_dict()

            # Convert image to RGB and save as single-page PDF
            with Image.open(self.input_path) as img:
                rgb = img.convert('RGB')
                rgb.save(self.output_path, format='PDF', resolution=150.0)

            return ProcessingResult(
                True,
                "Converted to PDF successfully",
                output_path=str(self.output_path),
                output_url=_build_output_url(Path(self.output_path)),
                metadata={'source_format': ext.lstrip('.')}
            ).to_dict()

        except Exception as e:
            logger.error(f"Error converting to PDF: {e}")
            return ProcessingResult(False, f"Failed to convert to PDF: {e}").to_dict()


class PDFTextExtractor(ToolBase):
    """Extract text content from PDF (optionally for given page ranges)."""

    def process(self, pages: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            with pdfplumber.open(str(self.input_path)) as pdf:
                total = len(pdf.pages)
                indices = _parse_page_ranges(pages, total) if pages else list(range(total))
                texts: List[Tuple[int, str]] = []
                for i in indices:
                    page = pdf.pages[i]
                    text = page.extract_text() or ""
                    texts.append((i + 1, text))

            combined = "\n\n".join([f"--- Page {i} ---\n{text}" for i, text in texts])
            meta = {
                'pages_extracted': [i for i, _ in texts],
                'total_pages': total
            }
            # For large texts, avoid attaching the entire content in metadata
            return ProcessingResult(True, "Text extracted successfully", metadata={**meta, 'text': combined}).to_dict()

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ProcessingResult(False, f"Failed to extract text: {e}").to_dict()
