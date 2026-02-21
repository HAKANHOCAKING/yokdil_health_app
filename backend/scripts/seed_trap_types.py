"""
Seed trap types database with 20 standard trap types
Run: python scripts/seed_trap_types.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.trap_type import TrapType


TRAP_TYPES_DATA = [
    {
        "code": "TRAP_MEANING_FLOW",
        "title_tr": "Anlam Akışı Kırılması",
        "title_en": "Meaning Flow Disruption",
        "description_tr": "Cümle mantığı/akışını bozar, sonuç doğal akmaz.",
        "description_en": "Disrupts sentence logic/flow, result doesn't flow naturally.",
        "category": "semantic",
        "display_order": 1,
        "related_tags": ["semantic_mismatch", "logical_inconsistency"]
    },
    {
        "code": "TRAP_LOGIC_RELATION",
        "title_tr": "Mantıksal İlişki Hatası",
        "title_en": "Logical Relation Error",
        "description_tr": "Bağlaç türü ve ilişki yanlış; however/therefore/whereas/because uyumsuzluğu.",
        "description_en": "Wrong connector type and relation; however/therefore/whereas/because mismatch.",
        "category": "logic",
        "display_order": 2,
        "related_tags": ["wrong_connector_type", "logical_inconsistency", "reversed_relation"]
    },
    {
        "code": "TRAP_CONTRAST_SIGNAL",
        "title_tr": "Zıtlık Sinyali Tuzağı",
        "title_en": "Contrast Signal Trap",
        "description_tr": "although/however/despite gibi zıtlık sinyallerini yanlış yönlendirir.",
        "description_en": "Misdirects contrast signals like although/however/despite.",
        "category": "logic",
        "display_order": 3,
        "related_tags": ["wrong_connector_type", "reversed_relation"]
    },
    {
        "code": "TRAP_CAUSE_EFFECT",
        "title_tr": "Neden–Sonuç Tuzağı",
        "title_en": "Cause-Effect Trap",
        "description_tr": "because/therefore/as a result zinciri ters ya da hatalı.",
        "description_en": "because/therefore/as a result chain is reversed or incorrect.",
        "category": "logic",
        "display_order": 4,
        "related_tags": ["reversed_relation", "logical_inconsistency"]
    },
    {
        "code": "TRAP_CONDITION_HYPOTHESIS",
        "title_tr": "Koşul–Varsayım Tuzağı",
        "title_en": "Condition-Hypothesis Trap",
        "description_tr": "if/unless/in case/as long as gibi yapılar yanlış gereklilik yaratır.",
        "description_en": "Structures like if/unless/in case/as long as create wrong requirements.",
        "category": "logic",
        "display_order": 5,
        "related_tags": ["logical_inconsistency"]
    },
    {
        "code": "TRAP_TIME_SEQUENCE",
        "title_tr": "Zaman–Sıralama Uyumsuzluğu",
        "title_en": "Time-Sequence Mismatch",
        "description_tr": "before/after/when/while veya olay sırası bozulur.",
        "description_en": "before/after/when/while or event sequence is disrupted.",
        "category": "grammar",
        "display_order": 6,
        "related_tags": ["sequence_error", "tense_mismatch"]
    },
    {
        "code": "TRAP_TENSE_ASPECT",
        "title_tr": "Tense/Aspect Uyumsuzluğu",
        "title_en": "Tense/Aspect Mismatch",
        "description_tr": "geçmiş/şimdi/gelecek, perfect/continuous uyumu bozulur.",
        "description_en": "past/present/future, perfect/continuous harmony is broken.",
        "category": "grammar",
        "display_order": 7,
        "related_tags": ["tense_mismatch", "aspect_mismatch"]
    },
    {
        "code": "TRAP_MODALITY_CERTAINTY",
        "title_tr": "Modal–Kesinlik Tuzağı",
        "title_en": "Modality-Certainty Trap",
        "description_tr": "may/might/must/should/can kesinlik derecesi stem ile çatışır.",
        "description_en": "may/might/must/should/can certainty level conflicts with stem.",
        "category": "grammar",
        "display_order": 8,
        "related_tags": ["modality_mismatch"]
    },
    {
        "code": "TRAP_VOICE_AGREEMENT",
        "title_tr": "Çatı–Uyum (Active/Passive) Tuzağı",
        "title_en": "Voice Agreement Trap",
        "description_tr": "passive gerekiyorken active, ya da agent mantığı bozulur.",
        "description_en": "active when passive needed, or agent logic broken.",
        "category": "grammar",
        "display_order": 9,
        "related_tags": ["passive_active_mismatch"]
    },
    {
        "code": "TRAP_REFERENCE_PRONOUN",
        "title_tr": "Referans/Zamir Tuzağı",
        "title_en": "Reference/Pronoun Trap",
        "description_tr": "it/they/this/these gibi referanslar yanlış yere gider.",
        "description_en": "References like it/they/this/these point to wrong antecedent.",
        "category": "grammar",
        "display_order": 10,
        "related_tags": ["pronoun_reference_error"]
    },
    {
        "code": "TRAP_SV_AGREEMENT",
        "title_tr": "Özne–Yüklem Uyumsuzluğu",
        "title_en": "Subject-Verb Agreement Error",
        "description_tr": "tekil/çoğul veya ana-fiil uyumu bozulur.",
        "description_en": "singular/plural or main-verb agreement broken.",
        "category": "grammar",
        "display_order": 11,
        "related_tags": ["subject_verb_disagreement"]
    },
    {
        "code": "TRAP_PARALLELISM",
        "title_tr": "Paralellik/Structure Tuzağı",
        "title_en": "Parallelism/Structure Trap",
        "description_tr": "not only…but also / both…and gibi paralel yapı bozulur.",
        "description_en": "Parallel structure like not only…but also / both…and broken.",
        "category": "structural",
        "display_order": 12,
        "related_tags": ["broken_parallelism"]
    },
    {
        "code": "TRAP_RELATIVE_CLAUSE",
        "title_tr": "Relative Clause Tuzağı",
        "title_en": "Relative Clause Trap",
        "description_tr": "which/that/who/where vs yanlış bağlanır veya anlamı çarpıtır.",
        "description_en": "which/that/who/where wrongly attached or distorts meaning.",
        "category": "structural",
        "display_order": 13,
        "related_tags": ["wrong_relative_attachment"]
    },
    {
        "code": "TRAP_PREPOSITION_PATTERN",
        "title_tr": "Preposition/Pattern Tuzağı",
        "title_en": "Preposition/Pattern Trap",
        "description_tr": "associated with / risk of / exposure to gibi kalıplar yanlış.",
        "description_en": "Patterns like associated with / risk of / exposure to wrong.",
        "category": "structural",
        "display_order": 14,
        "related_tags": ["wrong_preposition_pattern"]
    },
    {
        "code": "TRAP_COLLOCATION",
        "title_tr": "Kolokasyon / Doğal Kullanım Tuzağı",
        "title_en": "Collocation/Natural Usage Trap",
        "description_tr": "akademik/doğal kullanım sırıtır, yanlış kelime eşleşmesi.",
        "description_en": "Academic/natural usage awkward, wrong word pairing.",
        "category": "semantic",
        "display_order": 15,
        "related_tags": ["unnatural_collocation"]
    },
    {
        "code": "TRAP_REGISTER_HEALTH",
        "title_tr": "Sağlık Alanı Register/Terminoloji Tuzağı",
        "title_en": "Health Domain Register/Terminology Trap",
        "description_tr": "Sağlık akademik dili dışına çıkar, yanlış terminoloji seçtirir.",
        "description_en": "Goes outside health academic language, wrong terminology choice.",
        "category": "domain",
        "display_order": 16,
        "related_tags": ["health_register_mismatch"]
    },
    {
        "code": "TRAP_SCOPE_QUANTIFIER",
        "title_tr": "Kapsam–Miktar Tuzağı",
        "title_en": "Scope-Quantifier Trap",
        "description_tr": "some/most/only/rarely gibi genelleme/aşırı iddia veya quantifier çatışması.",
        "description_en": "Generalization/overclaim with some/most/only/rarely or quantifier conflict.",
        "category": "semantic",
        "display_order": 17,
        "related_tags": ["overgeneralization", "overspecification"]
    },
    {
        "code": "TRAP_NEGATION",
        "title_tr": "Olumsuzluk Tuzağı",
        "title_en": "Negation Trap",
        "description_tr": "not/no/little/hardly ile polarity bozulur.",
        "description_en": "Polarity broken with not/no/little/hardly.",
        "category": "semantic",
        "display_order": 18,
        "related_tags": ["polarity_error"]
    },
    {
        "code": "TRAP_DEFINITION_EXPLANATION",
        "title_tr": "Tanım–Açıklama Tuzağı",
        "title_en": "Definition-Explanation Trap",
        "description_tr": "that is / namely / in other words yanlış açıklama yapar.",
        "description_en": "that is / namely / in other words makes wrong explanation.",
        "category": "semantic",
        "display_order": 19,
        "related_tags": ["semantic_mismatch"]
    },
    {
        "code": "TRAP_TOPIC_DRIFT",
        "title_tr": "Konu Kaydırma Tuzağı",
        "title_en": "Topic Drift Trap",
        "description_tr": "Cümleyi başka temaya çeker; sağlık bağlamından kopar.",
        "description_en": "Pulls sentence to different topic; breaks from health context.",
        "category": "semantic",
        "display_order": 20,
        "related_tags": ["topic_drift"]
    },
]


async def seed_trap_types():
    """Seed trap types table"""
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding trap types...")
        
        # Check if already seeded
        from sqlalchemy import select
        result = await db.execute(select(TrapType))
        existing = result.scalars().all()
        
        if existing:
            print(f"⚠️  Found {len(existing)} existing trap types. Skipping seed.")
            print("   (Delete trap_types table to re-seed)")
            return
        
        # Insert all trap types
        for trap_data in TRAP_TYPES_DATA:
            trap_type = TrapType(**trap_data)
            db.add(trap_type)
        
        await db.commit()
        
        print(f"✅ Seeded {len(TRAP_TYPES_DATA)} trap types")
        
        # Print summary
        print("\n📊 Trap Types by Category:")
        from collections import Counter
        categories = Counter(t["category"] for t in TRAP_TYPES_DATA)
        for cat, count in categories.items():
            print(f"   {cat}: {count}")
        
        print("\n🎯 Standard Reason Tags (20):")
        from app.services.trap_analyzer_enhanced import REASON_TAGS
        for i, tag in enumerate(REASON_TAGS, 1):
            print(f"   {i}. {tag}")


if __name__ == "__main__":
    asyncio.run(seed_trap_types())
