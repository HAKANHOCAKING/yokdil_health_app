"""Add vocabulary and SRS tables

Revision ID: 001_vocab_srs
Revises: None
Create Date: 2026-02-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_vocab_srs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # VocabSet
    op.create_table(
        'vocab_sets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source_pdf_id', sa.String(255), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('word_count', sa.Integer(), default=0, nullable=False),
        sa.Column('status', sa.String(50), default='draft', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_vocab_sets_status', 'vocab_sets', ['status'])

    # VocabWord
    op.create_table(
        'vocab_words',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('set_id', sa.String(255), sa.ForeignKey('vocab_sets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('english', sa.String(500), nullable=False),
        sa.Column('turkish', sa.String(500), nullable=False),
        sa.Column('example_sentence', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), default=1.0, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_vocab_words_set_id', 'vocab_words', ['set_id'])

    # VocabProgress (SM-2)
    op.create_table(
        'vocab_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('word_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vocab_words.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ease_factor', sa.Float(), default=2.5, nullable=False),
        sa.Column('interval', sa.Integer(), default=0, nullable=False),
        sa.Column('repetition', sa.Integer(), default=0, nullable=False),
        sa.Column('next_review_date', sa.Date(), nullable=True),
        sa.Column('last_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('mastery_level', sa.Enum('new', 'learning', 'review', 'mastered', name='masterylevel'), default='new', nullable=False),
        sa.Column('total_reviews', sa.Integer(), default=0, nullable=False),
        sa.Column('correct_count', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_vocab_progress_user_id', 'vocab_progress', ['user_id'])
    op.create_index('ix_vocab_progress_word_id', 'vocab_progress', ['word_id'])
    op.create_index('ix_vocab_progress_mastery', 'vocab_progress', ['mastery_level'])

    # StudySession
    op.create_table(
        'study_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mode', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('words_studied', sa.Integer(), default=0, nullable=False),
        sa.Column('correct_count', sa.Integer(), default=0, nullable=False),
    )
    op.create_index('ix_study_sessions_user_id', 'study_sessions', ['user_id'])

    # StudyReview
    op.create_table(
        'study_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('study_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('word_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vocab_words.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quality', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('time_spent_ms', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_study_reviews_session_id', 'study_reviews', ['session_id'])
    op.create_index('ix_study_reviews_word_id', 'study_reviews', ['word_id'])

    # DailyStreak
    op.create_table(
        'daily_streaks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('current_streak', sa.Integer(), default=0, nullable=False),
        sa.Column('longest_streak', sa.Integer(), default=0, nullable=False),
        sa.Column('last_study_date', sa.Date(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_daily_streaks_user_id', 'daily_streaks', ['user_id'])


def downgrade() -> None:
    op.drop_table('daily_streaks')
    op.drop_table('study_reviews')
    op.drop_table('study_sessions')
    op.drop_table('vocab_progress')
    op.drop_table('vocab_words')
    op.drop_table('vocab_sets')
    op.execute("DROP TYPE IF EXISTS masterylevel")
