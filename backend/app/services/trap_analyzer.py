"""
Trap Analyzer Service - AI-powered ÖSYM trap detection and explanation
"""
from typing import Dict, Optional
from app.core.config import settings


class TrapAnalyzerService:
    """Service for analyzing incorrect options and identifying trap types"""
    
    # Trap type categories
    TRAP_TYPES = {
        "yakın_anlam_tuzağı": "Near-synonym trap - semantically close but contextually wrong",
        "gramer_tuzağı": "Grammar trap - incorrect tense, voice, or structure",
        "bağlaç_tuzağı": "Conjunction trap - wrong logical connector",
        "register_tuzağı": "Register trap - inappropriate formality/informality",
        "neden_sonuç_tuzağı": "Cause-effect trap - reverses or breaks causal logic",
        "zıtlık_tuzağı": "Contrast trap - opposite meaning when continuation expected",
        "koşul_tuzağı": "Conditional trap - wrong conditional type",
        "referans_tuzağı": "Reference trap - pronoun/determiner mismatch",
        "aşırı_güçlü_tuzak": "Overgeneralization trap - too absolute (always/never)",
        "collocation_tuzağı": "Collocation trap - unnatural word combination",
    }
    
    def __init__(self):
        """Initialize OpenAI client if API key available"""
        self.use_ai = bool(getattr(settings, 'OPENAI_API_KEY', ''))
        if self.use_ai:
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
            except ImportError:
                self.use_ai = False
    
    async def analyze_trap(
        self,
        stem: str,
        correct_option: str,
        wrong_option: str,
    ) -> Dict:
        """
        Analyze why an incorrect option is a trap
        
        Returns:
            {
                "trap_type": "yakın_anlam_tuzağı",
                "explanation_tr": "...",
                "explanation_en": "...",
                "reasoning_points": [
                    {"type": "semantic", "detail": "..."},
                    {"type": "collocation", "detail": "..."}
                ]
            }
        """
        if self.use_ai:
            return await self._ai_analyze_trap(stem, correct_option, wrong_option)
        else:
            return self._rule_based_analyze_trap(stem, correct_option, wrong_option)
    
    async def _ai_analyze_trap(self, stem: str, correct_option: str, wrong_option: str) -> Dict:
        """AI-powered trap analysis using GPT"""
        
        prompt = f"""You are an expert in YÖKDİL (Turkish academic English exam) question analysis.

Analyze this sentence completion question:

SENTENCE (with blank): {stem}
CORRECT ANSWER: {correct_option}
INCORRECT OPTION: {wrong_option}

Your task:
1. Identify the PRIMARY trap type from these categories:
   - yakın_anlam_tuzağı (near-synonym trap)
   - gramer_tuzağı (grammar trap)
   - bağlaç_tuzağı (conjunction trap)
   - register_tuzağı (register/formality trap)
   - neden_sonuç_tuzağı (cause-effect trap)
   - zıtlık_tuzağı (contrast trap)
   - koşul_tuzağı (conditional trap)
   - referans_tuzağı (reference/pronoun trap)
   - aşırı_güçlü_tuzak (overgeneralization trap)
   - collocation_tuzağı (collocation trap)

2. Explain in TURKISH why this option is wrong (2-3 sentences, clear and educational)
3. Provide reasoning points

Response format (JSON):
{{
  "trap_type": "selected_trap_type",
  "explanation_tr": "Türkçe açıklama",
  "explanation_en": "English explanation",
  "reasoning_points": [
    {{"type": "semantic/grammar/logical", "detail": "specific reason"}},
    {{"type": "collocation/context", "detail": "specific reason"}}
  ]
}}

IMPORTANT: 
- Be specific to THIS question
- Reference exact words from the stem
- Keep explanations concise and clear
- Focus on why it's WRONG, not just what's RIGHT
"""
        
        try:
            import openai
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a YÖKDİL exam expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON response
            import json
            result = json.loads(result_text)
            
            return result
        
        except Exception as e:
            # Fallback to rule-based if AI fails
            print(f"AI analysis failed: {e}")
            return self._rule_based_analyze_trap(stem, correct_option, wrong_option)
    
    def _rule_based_analyze_trap(self, stem: str, correct_option: str, wrong_option: str) -> Dict:
        """Rule-based trap detection (fallback when no AI)"""
        
        # Simple heuristics
        trap_type = "yakın_anlam_tuzağı"  # Default
        
        # Check for conjunction traps
        conjunctions = ['however', 'therefore', 'moreover', 'nevertheless', 'thus', 'hence']
        if any(conj in wrong_option.lower() for conj in conjunctions):
            trap_type = "bağlaç_tuzağı"
        
        # Check for grammar traps (tense mismatches)
        if self._has_tense_mismatch(stem, wrong_option):
            trap_type = "gramer_tuzağı"
        
        # Check for absolute terms (overgeneralization)
        absolute_terms = ['always', 'never', 'all', 'none', 'every', 'completely']
        if any(term in wrong_option.lower() for term in absolute_terms):
            trap_type = "aşırı_güçlü_tuzak"
        
        explanation_tr = f"'{wrong_option}' seçeneği {trap_type} kategorisine girer. Cümlenin bağlamıyla uyuşmaz."
        explanation_en = f"Option '{wrong_option}' is a {trap_type}. It doesn't fit the sentence context."
        
        return {
            "trap_type": trap_type,
            "explanation_tr": explanation_tr,
            "explanation_en": explanation_en,
            "reasoning_points": [
                {
                    "type": "heuristic",
                    "detail": f"Rule-based detection identified {trap_type}"
                }
            ]
        }
    
    def _has_tense_mismatch(self, stem: str, option: str) -> bool:
        """Detect tense mismatches (simplified)"""
        past_indicators = ['was', 'were', 'had', 'did', 'been']
        present_indicators = ['is', 'are', 'has', 'have', 'does']
        
        stem_has_past = any(ind in stem.lower() for ind in past_indicators)
        option_has_present = any(ind in option.lower() for ind in present_indicators)
        
        return stem_has_past and option_has_present
