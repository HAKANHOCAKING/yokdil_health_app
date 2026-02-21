"""
PDF Parser Service - Extracts questions from uploaded PDFs
"""
import re
from typing import List, Dict, Optional
import pdfplumber
import io

from app.services.trap_analyzer import TrapAnalyzerService


class PDFParserService:
    """Service for parsing YÖKDİL exam PDFs"""
    
    def __init__(self):
        self.trap_analyzer = TrapAnalyzerService()
    
    async def parse_pdf(self, pdf_content: bytes, has_solutions: bool = False) -> List[Dict]:
        """
        Parse PDF and extract questions
        
        Returns:
            List of question dictionaries with structure:
            {
                "exam_date": "Mart 2018",
                "question_no": 15,
                "stem_text": "...",
                "blank_position": 8,
                "options": [{"letter": "A", "text": "...", "is_correct": False}, ...],
                "vocabulary": [{"term": "...", "definition": "..."}],
                "difficulty": "medium",
            }
        """
        questions = []
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n\n"
                
                # Parse questions from text
                questions = self._extract_questions(full_text, has_solutions)
                
                # Generate trap analysis for each question
                for question in questions:
                    await self._analyze_question_traps(question)
        
        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")
        
        return questions
    
    def _extract_questions(self, text: str, has_solutions: bool) -> List[Dict]:
        """Extract questions from PDF text"""
        questions = []
        
        # Pattern for YÖKDİL questions (simplified heuristic)
        # Real implementation would be more sophisticated
        
        # Split by common patterns: question numbers (1. 2. 3. etc.)
        question_blocks = re.split(r'\n(\d+)\.\s+', text)
        
        current_exam_date = self._extract_exam_date(text)
        
        for i in range(1, len(question_blocks), 2):
            if i + 1 >= len(question_blocks):
                break
            
            question_no = int(question_blocks[i])
            question_text = question_blocks[i + 1]
            
            # Extract stem and options
            stem, options, blank_pos = self._parse_question_block(question_text)
            
            if stem and options:
                # Determine correct answer if solutions provided
                correct_option = None
                if has_solutions:
                    correct_option = self._find_correct_answer(question_text, options)
                
                questions.append({
                    "exam_date": current_exam_date,
                    "question_no": question_no,
                    "stem_text": stem,
                    "blank_position": blank_pos,
                    "options": options,
                    "correct_option": correct_option,
                    "vocabulary": self._extract_vocabulary(question_text),
                    "difficulty": self._estimate_difficulty(stem, options),
                })
        
        return questions
    
    def _extract_exam_date(self, text: str) -> str:
        """Extract exam date from PDF text"""
        # Look for patterns like "Mart 2018", "Eylül 2019", etc.
        months_tr = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                     "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        
        for month in months_tr:
            pattern = rf"{month}\s+\d{{4}}"
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return "Unknown"
    
    def _parse_question_block(self, block: str) -> tuple:
        """Parse a single question block into stem and options"""
        # Find the sentence with blank (--------)
        blank_pattern = r'([^.]*?-{3,}[^.]*\.)'
        stem_match = re.search(blank_pattern, block)
        
        if not stem_match:
            return None, None, 0
        
        stem = stem_match.group(1).strip()
        
        # Count word position of blank
        words_before_blank = stem.split('----')[0].split()
        blank_position = len(words_before_blank)
        
        # Extract options (A) ... (B) ... etc.
        options = []
        option_pattern = r'\(([A-E])\)\s*([^\n(]+)'
        option_matches = re.findall(option_pattern, block)
        
        for letter, text in option_matches:
            options.append({
                "letter": letter,
                "text": text.strip(),
                "is_correct": False,  # Will be determined later
            })
        
        return stem, options, blank_position
    
    def _find_correct_answer(self, block: str, options: List[Dict]) -> Optional[str]:
        """Find correct answer from solution PDF"""
        # Look for patterns like "Cevap: A" or "Doğru cevap: B"
        answer_pattern = r'(?:Cevap|Doğru cevap|Answer):\s*([A-E])'
        match = re.search(answer_pattern, block, re.IGNORECASE)
        
        if match:
            correct_letter = match.group(1)
            # Mark correct option
            for opt in options:
                if opt["letter"] == correct_letter:
                    opt["is_correct"] = True
            return correct_letter
        
        return None
    
    def _extract_vocabulary(self, block: str) -> List[Dict]:
        """Extract vocabulary glossary from question"""
        vocabulary = []
        
        # Look for glossary section (usually at bottom)
        glossary_pattern = r'(?:Kelimeler|Vocabulary|Glossary):\s*([^\n]+)'
        match = re.search(glossary_pattern, block, re.IGNORECASE)
        
        if match:
            terms_text = match.group(1)
            # Parse "term: definition" pairs
            term_pairs = re.findall(r'([^:,]+):\s*([^,]+)', terms_text)
            
            for term, definition in term_pairs:
                vocabulary.append({
                    "term": term.strip(),
                    "definition_tr": definition.strip(),
                })
        
        return vocabulary
    
    def _estimate_difficulty(self, stem: str, options: List[Dict]) -> str:
        """Estimate question difficulty using heuristics"""
        # Simple heuristic: longer sentences and more complex structures = harder
        
        word_count = len(stem.split())
        avg_word_length = sum(len(word) for word in stem.split()) / max(word_count, 1)
        subordinate_clauses = stem.count(',') + stem.count(';')
        
        difficulty_score = 0
        
        if word_count > 30:
            difficulty_score += 1
        if avg_word_length > 6:
            difficulty_score += 1
        if subordinate_clauses > 2:
            difficulty_score += 1
        
        # Check for medical/academic vocabulary
        academic_indicators = ['therefore', 'however', 'furthermore', 'consequently', 
                               'nevertheless', 'moreover', 'thus', 'hence']
        if any(word in stem.lower() for word in academic_indicators):
            difficulty_score += 1
        
        if difficulty_score >= 3:
            return "hard"
        elif difficulty_score >= 1:
            return "medium"
        else:
            return "easy"
    
    async def _analyze_question_traps(self, question: Dict):
        """Generate trap analysis for question options"""
        if not question.get("correct_option"):
            return
        
        # Find correct option text
        correct_text = None
        for opt in question["options"]:
            if opt["is_correct"]:
                correct_text = opt["text"]
                break
        
        if not correct_text:
            return
        
        # Analyze each incorrect option
        for opt in question["options"]:
            if not opt["is_correct"]:
                trap_analysis = await self.trap_analyzer.analyze_trap(
                    stem=question["stem_text"],
                    correct_option=correct_text,
                    wrong_option=opt["text"],
                )
                opt["trap_analysis"] = trap_analysis
