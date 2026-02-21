# 🎯 TRAP TYPES SİSTEMİ - DOKÜMANTASYON

## Genel Bakış

YÖKDİL Health App'e **20 standart trap type** ve gelişmiş analiz sistemi eklendi.

---

## 📚 20 STANDART TRAP TYPES

### Semantic (Anlam) - 5 trap
1. **TRAP_MEANING_FLOW** - Anlam Akışı Kırılması
2. **TRAP_COLLOCATION** - Kolokasyon Tuzağı
3. **TRAP_SCOPE_QUANTIFIER** - Kapsam-Miktar Tuzağı
4. **TRAP_NEGATION** - Olumsuzluk Tuzağı
5. **TRAP_TOPIC_DRIFT** - Konu Kaydırma Tuzağı

### Logic (Mantık) - 5 trap
6. **TRAP_LOGIC_RELATION** - Mantıksal İlişki Hatası
7. **TRAP_CONTRAST_SIGNAL** - Zıtlık Sinyali Tuzağı
8. **TRAP_CAUSE_EFFECT** - Neden-Sonuç Tuzağı
9. **TRAP_CONDITION_HYPOTHESIS** - Koşul-Varsayım Tuzağı
10. **TRAP_DEFINITION_EXPLANATION** - Tanım-Açıklama Tuzağı

### Grammar (Gramer) - 6 trap
11. **TRAP_TIME_SEQUENCE** - Zaman-Sıralama Uyumsuzluğu
12. **TRAP_TENSE_ASPECT** - Tense/Aspect Uyumsuzluğu
13. **TRAP_MODALITY_CERTAINTY** - Modal-Kesinlik Tuzağı
14. **TRAP_VOICE_AGREEMENT** - Çatı-Uyum Tuzağı
15. **TRAP_REFERENCE_PRONOUN** - Referans/Zamir Tuzağı
16. **TRAP_SV_AGREEMENT** - Özne-Yüklem Uyumsuzluğu

### Structural (Yapısal) - 3 trap
17. **TRAP_PARALLELISM** - Paralellik Tuzağı
18. **TRAP_RELATIVE_CLAUSE** - Relative Clause Tuzağı
19. **TRAP_PREPOSITION_PATTERN** - Preposition/Pattern Tuzağı

### Domain (Alan) - 1 trap
20. **TRAP_REGISTER_HEALTH** - Sağlık Terminoloji Tuzağı

---

## 🏷️ 20 STANDART REASON TAGS

Her yanlış şık için **1-3 reason tag** seçilir:

1. semantic_mismatch
2. logical_inconsistency
3. wrong_connector_type
4. reversed_relation
5. tense_mismatch
6. aspect_mismatch
7. modality_mismatch
8. passive_active_mismatch
9. pronoun_reference_error
10. subject_verb_disagreement
11. broken_parallelism
12. wrong_relative_attachment
13. wrong_preposition_pattern
14. unnatural_collocation
15. health_register_mismatch
16. overgeneralization
17. overspecification
18. polarity_error
19. sequence_error
20. topic_drift

---

## 🤖 AI ANALIZ MOTORU

### Input
```python
stem = "Recent studies suggest that regular exercise ------- chronic disease risk."
options = [
    {"letter": "A", "text": "reduces", "is_correct": True},
    {"letter": "B", "text": "increases", "is_correct": False},
    {"letter": "C", "text": "prevents", "is_correct": False},
]
```

### Output Format
```json
{
  "correct_analysis": {
    "option_letter": "A",
    "explanation_tr": "4-6 cümle açıklama: 1) ilişki türü 2) kanıt 3) neden doğru",
    "reasoning_points": [
      {"type": "relation_type", "detail": "neden-sonuç ilişkisi"},
      {"type": "evidence", "detail": "stem'den 'studies suggest'"},
      {"type": "why_correct", "detail": "'reduces' anlamsal uyum"}
    ],
    "evidence_snippets": [
      {"text": "studies suggest that", "position": "beginning"}
    ]
  },
  "wrong_analyses": [
    {
      "option_letter": "B",
      "trap_type": "TRAP_CONTRAST_SIGNAL",
      "explanation_tr": "'increases' zıt anlam yaratır ve mantık bozulur",
      "reason_tags": ["semantic_mismatch", "reversed_relation"],
      "evidence_snippets": [
        {"text": "exercise", "position": "middle"}
      ],
      "confidence": 90
    },
    {
      "option_letter": "C",
      "trap_type": "TRAP_SCOPE_QUANTIFIER",
      "explanation_tr": "'prevents' aşırı güçlü iddia, 'reduces' daha uygun",
      "reason_tags": ["overspecification"],
      "evidence_snippets": [
        {"text": "chronic disease risk", "position": "end"}
      ],
      "confidence": 85
    }
  ]
}
```

### Hallucination Prevention
✅ **Tüm evidence_snippets stem'den çıkarılır**
✅ **Evidence validation: fuzzy match ile kontrol**
✅ **Max 12 kelime per snippet**

---

## 📊 TEACHER DASHBOARD METRİKLERİ

### 1. Trap Performance (accuracy_by_trap_type)
```
GET /api/v1/analytics-enhanced/trap-performance?days=30&class_id={uuid}

Response:
{
  "trap_performance": [
    {
      "trap_code": "TRAP_LOGIC_RELATION",
      "trap_title_tr": "Mantıksal İlişki Hatası",
      "category": "logic",
      "accuracy": 0.58,
      "total_attempts": 45,
      "avg_time_seconds": 95.3
    }
  ],
  "top_5_weakest": [...]
}
```

### 2. Student-Trap Heatmap
```
GET /api/v1/analytics-enhanced/student-trap-heatmap?class_id={uuid}&days=30

Response:
{
  "heatmap": [
    {
      "student_id": "...",
      "trap_code": "TRAP_CAUSE_EFFECT",
      "accuracy": 0.45,
      "attempts": 12
    }
  ]
}
```

### 3. Top Traps Per Student
```
GET /api/v1/analytics-enhanced/top-traps-per-student?class_id={uuid}&limit=5

Response:
{
  "students": [
    {
      "student_id": "...",
      "student_name": "Ahmet Yılmaz",
      "top_weak_traps": [
        {
          "trap_code": "TRAP_LOGIC_RELATION",
          "trap_title": "Mantıksal İlişki Hatası",
          "accuracy": 0.42,
          "attempts": 15
        }
      ]
    }
  ]
}
```

### 4. Improvement Rate (Haftalık)
```python
# Weekly improvement calculation
week_1_accuracy = 0.60
week_2_accuracy = 0.68
improvement_rate = (week_2 - week_1) / week_1 * 100  # +13.3%
```

### 5. Confusion Pairs
En çok seçilen yanlış şıklar:
```json
{
  "confusion_pairs": [
    {
      "wrong_option": "B",
      "trap_type": "TRAP_CONTRAST_SIGNAL",
      "frequency": 45,
      "avg_confidence": "high"
    }
  ]
}
```

---

## 🎯 ÖDEV ATAMA (Assignment)

### Enhanced criteria_json
```json
{
  "branch": "health",
  "tags": ["anatomy", "epidemiology"],
  "trap_type_codes": ["TRAP_LOGIC_RELATION", "TRAP_CAUSE_EFFECT"],
  "difficulty_range": ["medium", "hard"],
  "exclude_mastered": true,
  "count": 20,
  "mastery_threshold": 0.85,
  "mastery_window_days": 30
}
```

### Mastery Logic
```python
# Bir trap "mastered" sayılır eğer:
# Son 30 günde accuracy >= 85% ise

if exclude_mastered:
    # O trap'leri içeren soruları dışla
    # Sadece NON-MASTERED trap'ler seç
```

### Example API Call
```python
POST /api/v1/teacher/assignments
{
  "class_id": "uuid",
  "title": "Mantıksal İlişkiler Ödevi",
  "criteria_json": {
    "trap_type_codes": ["TRAP_LOGIC_RELATION", "TRAP_CAUSE_EFFECT"],
    "exclude_mastered": true,
    "count": 15
  },
  "due_date": "2024-03-01T23:59:59Z"
}
```

---

## 🗄️ DATABASE SCHEMA

### New Tables

#### 1. trap_types
```sql
CREATE TABLE trap_types (
    id UUID PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    title_tr VARCHAR(255) NOT NULL,
    title_en VARCHAR(255),
    description_tr TEXT NOT NULL,
    description_en TEXT,
    category VARCHAR(50) NOT NULL,  -- semantic, logic, grammar, structural, domain
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    examples JSONB,
    related_tags JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed with 20 standard trap types
```

#### 2. trap_analyses_enhanced
```sql
CREATE TABLE trap_analyses_enhanced (
    id UUID PRIMARY KEY,
    option_id UUID REFERENCES options(id) UNIQUE NOT NULL,
    trap_type_id UUID REFERENCES trap_types(id) NOT NULL,
    explanation_tr TEXT NOT NULL,
    explanation_en TEXT,
    evidence_snippets JSONB NOT NULL,  -- [{"text": "...", "position": "..."}]
    reason_tags JSONB NOT NULL,  -- ["semantic_mismatch", ...]
    confidence_score INTEGER DEFAULT 80,
    analysis_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. question_explanations
```sql
CREATE TABLE question_explanations (
    id UUID PRIMARY KEY,
    question_id UUID REFERENCES questions(id) UNIQUE NOT NULL,
    correct_reason_tr TEXT NOT NULL,
    correct_reason_en TEXT,
    correct_reasoning_points JSONB NOT NULL,
    key_evidence_snippets JSONB NOT NULL,
    analysis_version VARCHAR(20) DEFAULT 'v2.0',
    generated_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. assignments (enhanced)
```sql
ALTER TABLE assignments ADD COLUMN criteria_json JSONB NOT NULL;
-- Enhanced structure with trap_type_codes, exclude_mastered, etc.
```

---

## 🚀 KULLANIM

### 1. Seed Trap Types
```bash
cd backend
python scripts/seed_trap_types.py

# Output:
# 🌱 Seeding trap types...
# ✅ Seeded 20 trap types
# 📊 Trap Types by Category:
#    semantic: 5
#    logic: 5
#    grammar: 6
#    structural: 3
#    domain: 1
```

### 2. Analyze Question
```python
from app.services.trap_analyzer_enhanced import TrapAnalyzerEnhanced

analyzer = TrapAnalyzerEnhanced()
analysis = await analyzer.analyze_question_complete(stem, options)

# Returns: correct_analysis + wrong_analyses with trap types
```

### 3. Create Assignment
```python
from app.services.assignment_builder import AssignmentBuilder

builder = AssignmentBuilder(db, tenant_id)
question_ids = await builder.build_assignment(
    criteria={
        "trap_type_codes": ["TRAP_LOGIC_RELATION"],
        "exclude_mastered": True,
        "count": 20
    },
    student_ids=[...],
)
```

### 4. Get Analytics
```bash
# Teacher dashboard
GET /api/v1/analytics-enhanced/trap-performance?class_id={uuid}&days=30

# Trap heatmap
GET /api/v1/analytics-enhanced/student-trap-heatmap?class_id={uuid}

# Top weak traps per student
GET /api/v1/analytics-enhanced/top-traps-per-student?class_id={uuid}
```

---

## 📈 EXPECTED IMPACT

### Before (Generic Traps)
- ❌ 10-15 farklı trap isimlendirmesi (tutarsız)
- ❌ Manuel etiketleme gerekiyor
- ❌ Teacher hangi trap'te zayıf bilmiyor
- ❌ Ödev atarken trap bazlı seçim yok

### After (Standardized Traps)
- ✅ **20 standart trap type** (tüm ÖSYM pattern'leri kapsıyor)
- ✅ **AI otomatik etiketleme** (evidence-based, no hallucination)
- ✅ **Teacher dashboard**: trap × student heatmap
- ✅ **Smart assignment**: exclude mastered traps
- ✅ **Progress tracking**: improvement rate by trap

---

## 🧪 TEST SCENARIOS

### Scenario 1: Student Performance
```python
# Ahmet'in son 30 gündeki trap performansı
{
  "TRAP_LOGIC_RELATION": {"accuracy": 0.58, "attempts": 23},
  "TRAP_CAUSE_EFFECT": {"accuracy": 0.72, "attempts": 18},
  "TRAP_COLLOCATION": {"accuracy": 0.85, "attempts": 15}  # MASTERED
}

# Ödev oluştur (exclude_mastered=true)
→ TRAP_COLLOCATION içeren sorular DÜŞ
→ TRAP_LOGIC_RELATION ve TRAP_CAUSE_EFFECT soruları SEÇ
```

### Scenario 2: Class Heatmap
```
            LOGIC_REL  CAUSE_EFFECT  COLLOCATION
Ahmet         58%        72%           85%
Ayşe          45%        68%           78%
Mehmet        82%        55%           91%
```
→ Teacher görür: "Ayşe LOGIC_REL'de zayıf, Mehmet CAUSE_EFFECT'te zayıf"

---

## 🎓 BEST PRACTICES

### 1. Evidence Extraction
✅ **DO**: Extract exact words from stem
❌ **DON'T**: Add external knowledge

```python
# ✅ Good
evidence = "studies suggest that"  # Direct from stem

# ❌ Bad
evidence = "research shows exercise is beneficial"  # Hallucination
```

### 2. Trap Type Selection
✅ **DO**: Choose 1 primary trap type
❌ **DON'T**: Assign multiple trap types to same option

### 3. Reason Tags
✅ **DO**: Use 1-3 specific tags
❌ **DON'T**: Use all 20 tags

### 4. Mastery Threshold
✅ **DO**: Use 85% default (adjustable)
❌ **DON'T**: Set too low (70%) or too high (95%)

---

## 📦 FILES CREATED

1. `backend/app/models/trap_type.py` - Models
2. `backend/app/services/trap_analyzer_enhanced.py` - AI analyzer
3. `backend/app/services/assignment_builder.py` - Assignment logic
4. `backend/app/api/v1/endpoints/analytics_enhanced.py` - Teacher metrics
5. `backend/scripts/seed_trap_types.py` - Seed script
6. `TRAP_SYSTEM_DOCUMENTATION.md` - This file

---

## 🔜 NEXT STEPS

1. ✅ Database migration (add new tables)
2. ✅ Run seed script (20 trap types)
3. ⏳ Integrate AI analyzer into PDF import
4. ⏳ Update teacher dashboard UI (trap heatmap)
5. ⏳ Test assignment builder with real data

---

**Version**: 1.0.0  
**Last Updated**: 2024-02-17  
**Status**: ✅ Implementation Complete
