"""
OCR Service - Extract text from page images using Tesseract
"""
import io
import logging
from PIL import Image
import pytesseract

from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """Extract text from images using Tesseract OCR"""

    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

    def extract_text(self, image_bytes: bytes, lang: str = "eng+tur") -> str:
        """
        Extract text from PNG image bytes.

        Args:
            image_bytes: PNG image data
            lang: Tesseract language codes (eng+tur for English+Turkish)

        Returns:
            Extracted text string
        """
        image = Image.open(io.BytesIO(image_bytes))

        # Pre-process: convert to grayscale for better OCR
        if image.mode != "L":
            image = image.convert("L")

        try:
            text = pytesseract.image_to_string(
                image,
                lang=lang,
                config="--oem 3 --psm 6",  # LSTM engine, uniform block
            )
            logger.info(f"OCR extracted {len(text)} characters")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""

    def extract_with_confidence(self, image_bytes: bytes, lang: str = "eng+tur") -> list[dict]:
        """
        Extract text with per-word confidence scores.

        Returns:
            List of dicts: [{"text": "word", "confidence": 85.5, "left": 10, "top": 20}, ...]
        """
        image = Image.open(io.BytesIO(image_bytes))

        if image.mode != "L":
            image = image.convert("L")

        try:
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                config="--oem 3 --psm 6",
                output_type=pytesseract.Output.DICT,
            )

            results = []
            for i in range(len(data["text"])):
                word = data["text"][i].strip()
                if not word:
                    continue
                conf = float(data["conf"][i])
                if conf < 0:
                    continue
                results.append({
                    "text": word,
                    "confidence": conf,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                })

            return results
        except Exception as e:
            logger.error(f"OCR with confidence failed: {e}")
            return []
