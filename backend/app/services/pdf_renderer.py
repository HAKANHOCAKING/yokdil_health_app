"""
PDF Renderer Service - Renders PDF pages as images using PyMuPDF
On-demand rendering with disk caching
"""
import os
import io
import hashlib
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)

# Cache directory for rendered page images
CACHE_DIR = Path("data/pdf_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class PDFRendererService:
    """Renders PDF pages as PNG images with caching"""

    def __init__(self, dpi: int = 200):
        self.dpi = dpi
        self.zoom = dpi / 72.0  # PDF default is 72 DPI

    def _cache_key(self, pdf_content_hash: str, page_num: int) -> str:
        return f"{pdf_content_hash}_p{page_num}_{self.dpi}dpi"

    def _cache_path(self, cache_key: str) -> Path:
        return CACHE_DIR / f"{cache_key}.png"

    def _hash_content(self, pdf_content: bytes) -> str:
        return hashlib.sha256(pdf_content).hexdigest()[:16]

    def get_page_count(self, pdf_content: bytes) -> int:
        """Get total number of pages in PDF"""
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        count = len(doc)
        doc.close()
        return count

    def render_page(self, pdf_content: bytes, page_num: int) -> bytes:
        """
        Render a single PDF page as PNG.
        Uses cache if available, otherwise renders and caches.

        Args:
            pdf_content: Raw PDF bytes
            page_num: 0-indexed page number

        Returns:
            PNG image bytes
        """
        content_hash = self._hash_content(pdf_content)
        cache_key = self._cache_key(content_hash, page_num)
        cache_path = self._cache_path(cache_key)

        # Check cache
        if cache_path.exists():
            logger.debug(f"Cache hit for page {page_num}")
            return cache_path.read_bytes()

        # Render page
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        if page_num < 0 or page_num >= len(doc):
            doc.close()
            raise ValueError(f"Page {page_num} out of range (0-{len(doc)-1})")

        page = doc[page_num]
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PNG bytes
        png_bytes = pix.tobytes("png")

        doc.close()

        # Save to cache
        cache_path.write_bytes(png_bytes)
        logger.info(f"Rendered and cached page {page_num} ({len(png_bytes)} bytes)")

        return png_bytes

    def render_all_pages(self, pdf_content: bytes) -> list[dict]:
        """
        Render all pages of a PDF.

        Returns:
            List of dicts: [{"page": 0, "size": 12345, "cached": True/False}, ...]
        """
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        total = len(doc)
        doc.close()

        results = []
        for page_num in range(total):
            content_hash = self._hash_content(pdf_content)
            cache_key = self._cache_key(content_hash, page_num)
            cache_path = self._cache_path(cache_key)
            was_cached = cache_path.exists()

            png_bytes = self.render_page(pdf_content, page_num)
            results.append({
                "page": page_num,
                "size": len(png_bytes),
                "cached": was_cached,
            })

        return results

    def get_page_image_if_cached(self, pdf_content: bytes, page_num: int) -> Optional[bytes]:
        """Get cached page image without rendering"""
        content_hash = self._hash_content(pdf_content)
        cache_key = self._cache_key(content_hash, page_num)
        cache_path = self._cache_path(cache_key)

        if cache_path.exists():
            return cache_path.read_bytes()
        return None

    def clear_cache(self, pdf_content: Optional[bytes] = None):
        """Clear cache for a specific PDF or all cached images"""
        if pdf_content:
            content_hash = self._hash_content(pdf_content)
            for f in CACHE_DIR.glob(f"{content_hash}_*.png"):
                f.unlink()
                logger.info(f"Cleared cache: {f.name}")
        else:
            for f in CACHE_DIR.glob("*.png"):
                f.unlink()
            logger.info("Cleared all PDF cache")
