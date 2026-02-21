"""
Enhanced Trap Analyzer Service
Standardized 20 trap types + evidence-based analysis
"""
from typing import Dict, List, Optional
import openai
import json
import re
from app.core.config import settings


# Standard reason tags (20 tags)
REASON_TAGS = [
    "semantic_mismatch",
    "logical_inconsistency",
    "wrong_connector_type",
    "reversed_relation",
    "tense_mismatch",
    "aspect_mismatch",
    "modality_mismatch",
    "passive_active_mismatch",
    "pronoun_reference_error",
    "subject_verb_disagreement",
    "broken_parallelism",
    "wrong_relative_attachment",
    "wrong_preposition_pattern",
    "unnatural_collocation",
    "health_register_mismatch",
    "overgeneralization",
    "overspecification",
    "polarity_error",
    "sequence_error",
    "topic_drift",
]


class TrapAnalyzerEnhanced:
    """Enhanced trap analyzer with standardized trap types"""
    
    def __init__(self):
        self.use_ai = bool(settings.OPENAI_API_KEY)
        if self.use_ai:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def analyze_question_complete(
        self,
        stem: str,
        options: List[Dict],  # [{"letter": "A", "text": "...", "is_correct": bool}]
    ) -> Dict:
        """
        Complete question analysis:
        - Correct answer reasoning (4-6 sentences)
        - Each wrong option analysis (2-4 sentences + trap + reasons + evidence)
        """
        if not self.use_ai:
            return self._fallback_analysis(stem, options)
        
        prompt = self._build_analysis_prompt(stem, options)
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            
            result_text = response.choices[0].message.content
            analysis = json.loads(result_text)
            
            # Validate and sanitize
            return self._validate_analysis(analysis, stem, options)
        
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._fallback_analysis(stem, options)
    
    def _get_system_prompt(self) -> str:
        """System prompt with trap types and guidelines"""
        trap_types_desc = """
20 STANDART TRAP TYPES:
1. TRAP_MEANING_FLOW - Anlam akışı kırılması
2. TRAP_LOGIC_RELATION - Mantıksal ilişki hatası (neden-sonuç/zıtlık)
3. TRAP_CONTRAST_SIGNAL - Zıtlık sinyali tuzağı (although/however/despite)
4. TRAP_CAUSE_EFFECT - Neden-sonuç zinciri hatası
5. TRAP_CONDITION_HYPOTHESIS - Koşul-varsayım tuzağı (if/unless)
6. TRAP_TIME_SEQUENCE - Zaman-sıralama uyumsuzluğu
7. TRAP_TENSE_ASPECT - Tense/aspect uyumsuzluğu
8. TRAP_MODALITY_CERTAINTY - Modal-kesinlik tuzağı (may/must/should)
9. TRAP_VOICE_AGREEMENT - Çatı-uyum tuzağı (active/passive)
10. TRAP_REFERENCE_PRONOUN - Referans/zamir tuzağı
11. TRAP_SV_AGREEMENT - Özne-yüklem uyumsuzluğu
12. TRAP_PARALLELISM - Paralellik/yapı tuzağı
13. TRAP_RELATIVE_CLAUSE - Relative clause tuzağı
14. TRAP_PREPOSITION_PATTERN - Preposition/pattern tuzağı
15. TRAP_COLLOCATION - Kolokasyon tuzağı
16. TRAP_REGISTER_HEALTH - Sağlık terminoloji tuzağı
17. TRAP_SCOPE_QUANTIFIER - Kapsam-miktar tuzağı (some/most/only)
18. TRAP_NEGATION - Olumsuzluk tuzağı
19. TRAP_DEFINITION_EXPLANATION - Tanım-açıklama tuzağı
20. TRAP_TOPIC_DRIFT - Konu kaydırma tuzağı

REASON TAGS (1-3 per wrong option):
semantic_mismatch, logical_inconsistency, wrong_connector_type, reversed_relation,
tense_mismatch, aspect_mismatch, modality_mismatch, passive_active_mismatch,
pronoun_reference_error, subject_verb_disagreement, broken_parallelism,
wrong_relative_attachment, wrong_preposition_pattern, unnatural_collocation,
health_register_mismatch, overgeneralization, overspecification, polarity_error,
sequence_error, topic_drift

CRITICAL RULES:
1. Evidence ONLY from stem (no hallucination)
2. Evidence snippets: 1-2 pieces, max 12 words each
3. Correct reasoning: 4-6 sentences
4. Wrong option analysis: 2-4 sentences
5. Response must be valid JSON
"""
        return f"""You are a YÖKDİL sentence completion expert analyzing health/medical academic texts.

{trap_types_desc}

Your task: Provide comprehensive analysis in TURKISH."""
    
    def _build_analysis_prompt(self, stem: str, options: List[Dict]) -> str:
        """Build analysis prompt"""
        correct_option = next((opt for opt in options if opt["is_correct"]), None)
        wrong_options = [opt for opt in options if not opt["is_correct"]]
        
        prompt = f"""Analyze this YÖKDİL sentence completion question:

STEM: {stem}

OPTIONS:
"""
        for opt in options:
            status = "✓ CORRECT" if opt["is_correct"] else "✗ WRONG"
            prompt += f"({opt['letter']}) {opt['text']} [{status}]\n"
        
        prompt += """

Provide JSON response with this EXACT structure:

{
  "correct_analysis": {
    "option_letter": "A",
    "explanation_tr": "4-6 cümle: 1) ilişki türü 2) stem'den kanıt 3) neden doğru",
    "reasoning_points": [
      {"type": "relation_type", "detail": "neden-sonuç ilişkisi var"},
      {"type": "evidence", "detail": "stem'den spesifik kelime/cümle"},
      {"type": "why_correct", "detail": "bu yüzden doğru"}
    ],
    "evidence_snippets": [
      {"text": "exact words from stem", "position": "beginning/middle/end"}
    ]
  },
  "wrong_analyses": [
    {
      "option_letter": "B",
      "trap_type": "TRAP_LOGIC_RELATION",
      "explanation_tr": "2-4 cümle: trap türü + kanıt + neden yanlış",
      "reason_tags": ["wrong_connector_type", "logical_inconsistency"],
      "evidence_snippets": [
        {"text": "exact words from stem", "position": "middle"}
      ],
      "confidence": 85
    }
    // ... for each wrong option
  ]
}

REQUIREMENTS:
- ALL evidence from stem only (NO external info)
- Evidence snippets: max 12 words each
- Trap type: choose 1 from 20 standard types
- Reason tags: choose 1-3 from standard list
- Confidence: 0-100
- Turkish explanation: clear and educational
"""
        return prompt
    
    def _validate_analysis(self, analysis: Dict, stem: str, options: List[Dict]) -> Dict:
        """Validate and sanitize AI response"""
        # Check structure
        if "correct_analysis" not in analysis or "wrong_analyses" not in analysis:
            raise ValueError("Invalid analysis structure")
        
        # Validate evidence snippets (must be in stem)
        for snippet in analysis["correct_analysis"].get("evidence_snippets", []):
            if not self._is_evidence_in_stem(snippet.get("text", ""), stem):
                print(f"WARNING: Evidence not in stem: {snippet}")
        
        for wrong in analysis["wrong_analyses"]:
            for snippet in wrong.get("evidence_snippets", []):
                if not self._is_evidence_in_stem(snippet.get("text", ""), stem):
                    print(f"WARNING: Evidence not in stem: {snippet}")
            
            # Validate trap_type
            if not wrong.get("trap_type", "").startswith("TRAP_"):
                wrong["trap_type"] = "TRAP_MEANING_FLOW"  # Default
            
            # Validate reason_tags
            wrong["reason_tags"] = [
                tag for tag in wrong.get("reason_tags", [])
                if tag in REASON_TAGS
            ][:3]  # Max 3 tags
            
            if not wrong["reason_tags"]:
                wrong["reason_tags"] = ["semantic_mismatch"]  # Default
        
        return analysis
    
    def _is_evidence_in_stem(self, evidence: str, stem: str) -> bool:
        """Check if evidence text exists in stem (fuzzy match)"""
        if not evidence or len(evidence) < 3:
            return True  # Skip very short
        
        # Normalize
        evidence_clean = re.sub(r'[^\w\s]', '', evidence.lower())
        stem_clean = re.sub(r'[^\w\s]', '', stem.lower())
        
        # Check if evidence words appear in stem (fuzzy)
        evidence_words = evidence_clean.split()
        if len(evidence_words) <= 2:
            return evidence_clean in stem_clean
        
        # For longer evidence, check if most words exist
        matches = sum(1 for word in evidence_words if word in stem_clean)
        return matches >= len(evidence_words) * 0.7  # 70% threshold
    
    def _fallback_analysis(self, stem: str, options: List[Dict]) -> Dict:
        """Fallback analysis when AI unavailable"""
        correct = next((opt for opt in options if opt["is_correct"]), options[0])
        wrong = [opt for opt in options if not opt["is_correct"]]
        
        return {
            "correct_analysis": {
                "option_letter": correct["letter"],
                "explanation_tr": f"'{correct['text']}' seçeneği cümlenin anlam akışına ve gramer yapısına uygun doğru cevaptır.",
                "reasoning_points": [
                    {"type": "relation_type", "detail": "Cümle yapısı ile uyumlu"},
                    {"type": "evidence", "detail": "Stem içeriği destekliyor"},
                    {"type": "why_correct", "detail": "Anlam ve gramer doğru"}
                ],
                "evidence_snippets": []
            },
            "wrong_analyses": [
                {
                    "option_letter": opt["letter"],
                    "trap_type": "TRAP_MEANING_FLOW",
                    "explanation_tr": f"'{opt['text']}' seçeneği anlam akışını bozar.",
                    "reason_tags": ["semantic_mismatch"],
                    "evidence_snippets": [],
                    "confidence": 70
                }
                for opt in wrong
            ]
        }
