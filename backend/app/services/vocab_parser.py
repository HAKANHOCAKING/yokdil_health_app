"""
Vocabulary Parser Service - Extract EN-TR word pairs from OCR text
Handles various formats: dash-separated, colon-separated, numbered lists
"""
import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Turkish special characters for language detection
TURKISH_CHARS = set("çğıöşüÇĞİÖŞÜ")


class VocabParserService:
    """Parse vocabulary word pairs from OCR-extracted text"""

    def parse_vocabulary(self, text: str) -> List[Dict]:
        """
        Extract English-Turkish word pairs from OCR text.

        Tries multiple patterns:
        1. "word - kelime" (dash separated)
        2. "word: kelime" (colon separated)
        3. "1. word - kelime" (numbered list)
        4. "word (kelime)" (parenthetical)

        Returns:
            List of dicts: [{"english": "...", "turkish": "...", "confidence": 0.8}, ...]
        """
        if not text or not text.strip():
            return []

        results = []

        # Try each pattern
        results.extend(self._parse_dash_separated(text))
        results.extend(self._parse_colon_separated(text))
        results.extend(self._parse_numbered_list(text))
        results.extend(self._parse_parenthetical(text))

        # Deduplicate by English word (case-insensitive)
        seen = set()
        unique = []
        for item in results:
            key = item["english"].lower().strip()
            if key not in seen and len(key) > 1:
                seen.add(key)
                unique.append(item)

        logger.info(f"Parsed {len(unique)} unique word pairs from text")
        return unique

    def _parse_dash_separated(self, text: str) -> List[Dict]:
        """Parse 'english - turkish' patterns"""
        results = []
        # Match: word(s) - word(s), allowing Turkish chars
        pattern = r'([A-Za-z][A-Za-z\s]*?)\s*[-–—]\s*([^\n]+)'

        for match in re.finditer(pattern, text):
            en = match.group(1).strip()
            tr = match.group(2).strip()

            # Remove trailing punctuation
            tr = re.sub(r'[;,\.\s]+$', '', tr)

            if self._is_valid_pair(en, tr):
                lang_en, lang_tr = self._assign_languages(en, tr)
                results.append({
                    "english": lang_en,
                    "turkish": lang_tr,
                    "confidence": 0.8,
                    "pattern": "dash",
                })

        return results

    def _parse_colon_separated(self, text: str) -> List[Dict]:
        """Parse 'english: turkish' patterns"""
        results = []
        pattern = r'([A-Za-z][A-Za-z\s]*?)\s*:\s*([^\n:]+)'

        for match in re.finditer(pattern, text):
            en = match.group(1).strip()
            tr = match.group(2).strip()
            tr = re.sub(r'[;,\.\s]+$', '', tr)

            if self._is_valid_pair(en, tr):
                lang_en, lang_tr = self._assign_languages(en, tr)
                results.append({
                    "english": lang_en,
                    "turkish": lang_tr,
                    "confidence": 0.7,
                    "pattern": "colon",
                })

        return results

    def _parse_numbered_list(self, text: str) -> List[Dict]:
        """Parse '1. english - turkish' or '1) english - turkish' patterns"""
        results = []
        pattern = r'\d+[.)]\s*([A-Za-z][A-Za-z\s]*?)\s*[-–—:]\s*([^\n]+)'

        for match in re.finditer(pattern, text):
            en = match.group(1).strip()
            tr = match.group(2).strip()
            tr = re.sub(r'[;,\.\s]+$', '', tr)

            if self._is_valid_pair(en, tr):
                lang_en, lang_tr = self._assign_languages(en, tr)
                results.append({
                    "english": lang_en,
                    "turkish": lang_tr,
                    "confidence": 0.85,
                    "pattern": "numbered",
                })

        return results

    def _parse_parenthetical(self, text: str) -> List[Dict]:
        """Parse 'english (turkish)' patterns"""
        results = []
        pattern = r'([A-Za-z][A-Za-z\s]*?)\s*\(([^)]+)\)'

        for match in re.finditer(pattern, text):
            en = match.group(1).strip()
            tr = match.group(2).strip()

            if self._is_valid_pair(en, tr):
                lang_en, lang_tr = self._assign_languages(en, tr)
                results.append({
                    "english": lang_en,
                    "turkish": lang_tr,
                    "confidence": 0.75,
                    "pattern": "parenthetical",
                })

        return results

    def _has_turkish_chars(self, text: str) -> bool:
        """Check if text contains Turkish-specific characters"""
        return bool(set(text) & TURKISH_CHARS)

    def _assign_languages(self, text1: str, text2: str) -> tuple:
        """
        Determine which text is English and which is Turkish.
        Returns (english, turkish)
        """
        t1_turkish = self._has_turkish_chars(text1)
        t2_turkish = self._has_turkish_chars(text2)

        if t2_turkish and not t1_turkish:
            return text1, text2
        elif t1_turkish and not t2_turkish:
            return text2, text1
        else:
            # Default: first is English, second is Turkish
            return text1, text2

    def _is_valid_pair(self, text1: str, text2: str) -> bool:
        """Validate that both parts look like real words"""
        if not text1 or not text2:
            return False
        if len(text1) < 2 or len(text2) < 2:
            return False
        if len(text1) > 100 or len(text2) > 100:
            return False
        # At least one should contain actual letters
        if not re.search(r'[a-zA-ZçğıöşüÇĞİÖŞÜ]', text1):
            return False
        if not re.search(r'[a-zA-ZçğıöşüÇĞİÖŞÜ]', text2):
            return False
        return True
