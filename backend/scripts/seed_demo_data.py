"""
Seed demo data for testing
Run: python scripts/seed_demo_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.question import Question, Option, Tag, VocabularyGlossary, QuestionTag
from app.models.user import User, Institution
from app.core.security import get_password_hash


async def seed_demo_data():
    """Seed demo questions and users"""
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding demo data...")

        # Create demo institution
        institution = Institution(
            name="Demo Üniversitesi",
            subscription_type="pro",
        )
        db.add(institution)
        await db.commit()
        await db.refresh(institution)
        print("✅ Institution created")

        # Create demo users
        demo_student = User(
            email="student@demo.com",
            hashed_password=get_password_hash("DemoPass123!"),
            full_name="Demo Öğrenci",
            role="student",
            institution_id=institution.id,
        )
        db.add(demo_student)

        demo_teacher = User(
            email="teacher@demo.com",
            hashed_password=get_password_hash("DemoPass123!"),
            full_name="Demo Öğretmen",
            role="teacher",
            institution_id=institution.id,
        )
        db.add(demo_teacher)

        demo_admin = User(
            email="admin@demo.com",
            hashed_password=get_password_hash("DemoPass123!"),
            full_name="Demo Admin",
            role="admin",
            institution_id=institution.id,
        )
        db.add(demo_admin)

        await db.commit()
        print("✅ Users created")

        # Create tags
        tags_data = [
            ("public_health", "topic"),
            ("epidemiology", "topic"),
            ("anatomy", "topic"),
            ("pharmacology", "topic"),
        ]

        tags = []
        for tag_name, category in tags_data:
            tag = Tag(name=tag_name, category=category)
            db.add(tag)
            tags.append(tag)

        await db.commit()
        print("✅ Tags created")

        # Create demo questions
        questions_data = [
            {
                "exam_date": "Mart 2018",
                "question_no": 1,
                "stem_text": "Recent studies suggest that regular physical activity ------- the risk of developing chronic diseases.",
                "blank_position": 8,
                "difficulty": "medium",
                "options": [
                    ("A", "reduces", True),
                    ("B", "increases", False),
                    ("C", "prevents", False),
                    ("D", "eliminates", False),
                    ("E", "avoids", False),
                ],
                "vocabulary": [
                    ("chronic diseases", "Kronik hastalıklar"),
                    ("physical activity", "Fiziksel aktivite"),
                ],
            },
            {
                "exam_date": "Eylül 2018",
                "question_no": 5,
                "stem_text": "The World Health Organization ------- new guidelines for managing diabetes in primary care settings.",
                "blank_position": 5,
                "difficulty": "easy",
                "options": [
                    ("A", "has published", True),
                    ("B", "will publish", False),
                    ("C", "was publishing", False),
                    ("D", "had published", False),
                    ("E", "publishes", False),
                ],
                "vocabulary": [
                    ("guidelines", "Kılavuzlar"),
                    ("diabetes", "Diyabet"),
                ],
            },
            {
                "exam_date": "Mart 2019",
                "question_no": 12,
                "stem_text": "Despite extensive research, the exact mechanism ------- Alzheimer's disease develops remains unclear.",
                "blank_position": 7,
                "difficulty": "hard",
                "options": [
                    ("A", "by which", True),
                    ("B", "in which", False),
                    ("C", "for which", False),
                    ("D", "on which", False),
                    ("E", "with which", False),
                ],
                "vocabulary": [
                    ("mechanism", "Mekanizma"),
                    ("Alzheimer's disease", "Alzheimer hastalığı"),
                ],
            },
        ]

        for q_data in questions_data:
            question = Question(
                exam_date=q_data["exam_date"],
                question_no=q_data["question_no"],
                stem_text=q_data["stem_text"],
                blank_position=q_data["blank_position"],
                difficulty=q_data["difficulty"],
            )
            db.add(question)
            await db.commit()
            await db.refresh(question)

            # Add options
            for letter, text, is_correct in q_data["options"]:
                option = Option(
                    question_id=question.id,
                    option_letter=letter,
                    option_text=text,
                    is_correct=is_correct,
                )
                db.add(option)

            # Add vocabulary
            for term, definition in q_data.get("vocabulary", []):
                vocab = VocabularyGlossary(
                    question_id=question.id,
                    term=term,
                    definition_tr=definition,
                )
                db.add(vocab)

            # Add tags (first tag for each question)
            if tags:
                question_tag = QuestionTag(
                    question_id=question.id,
                    tag_id=tags[0].id,
                )
                db.add(question_tag)

            await db.commit()
            print(f"✅ Question {q_data['question_no']} created")

        print("\n🎉 Demo data seeded successfully!")
        print("\n📧 Demo Accounts:")
        print("   Student: student@demo.com / DemoPass123!")
        print("   Teacher: teacher@demo.com / DemoPass123!")
        print("   Admin:   admin@demo.com / DemoPass123!")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
