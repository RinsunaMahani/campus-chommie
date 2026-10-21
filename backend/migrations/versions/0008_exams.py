"""A student's exams.

Revision ID: 0008_exams
Revises: 0007_timetable
Create Date: 2026-10-20

student.exam_entries holds the exam papers a student keeps (picked from their university's exam list or
typed): module, its name and paper, date, start time, minutes, venue; nothing about them. A row goes with its
account (ON DELETE CASCADE). Written by hand to match the model, with its CHECK constraint (autogenerate
doesn't compare them).
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0008_exams'
down_revision = '0007_timetable'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('exam_entries',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('module', sa.String(length=20), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=True),
    sa.Column('paper', sa.String(length=80), nullable=True),
    sa.Column('exam_on', sa.Date(), nullable=False),
    sa.Column('starts_at', sa.Time(), nullable=False),
    sa.Column('minutes', sa.SmallInteger(), nullable=True),
    sa.Column('venue', sa.String(length=80), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('minutes IS NULL OR minutes BETWEEN 1 AND 480', name='ck_exam_entries_minutes'),
    sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='student'
    )
    op.create_index('ix_exam_entries_user', 'exam_entries', ['user_id', 'exam_on', 'starts_at'],
                    unique=False, schema='student')


def downgrade():
    op.drop_index('ix_exam_entries_user', table_name='exam_entries', schema='student')
    op.drop_table('exam_entries', schema='student')
