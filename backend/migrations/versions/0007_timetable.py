"""A student's timetable.

Revision ID: 0007_timetable
Revises: 0006_saved_funding
Create Date: 2026-10-20

student.timetable_entries holds the classes a student enters for their week: module, kind, weekday,
start and end time, venue; nothing about them. A row goes with its account (ON DELETE CASCADE).
Written by hand to match the model, with its CHECK constraints (autogenerate doesn't compare them).
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0007_timetable'
down_revision = '0006_saved_funding'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('timetable_entries',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('module', sa.String(length=20), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=True),
    sa.Column('kind', sa.String(length=12), nullable=False),
    sa.Column('weekday', sa.SmallInteger(), nullable=False),
    sa.Column('starts_at', sa.Time(), nullable=False),
    sa.Column('ends_at', sa.Time(), nullable=False),
    sa.Column('venue', sa.String(length=80), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('weekday BETWEEN 0 AND 6', name='ck_timetable_entries_weekday'),
    sa.CheckConstraint('ends_at > starts_at', name='ck_timetable_entries_order'),
    sa.CheckConstraint("kind IN ('lecture', 'tutorial', 'practical', 'other')", name='ck_timetable_entries_kind'),
    sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='student'
    )
    op.create_index('ix_timetable_entries_user', 'timetable_entries', ['user_id', 'weekday', 'starts_at'],
                    unique=False, schema='student')


def downgrade():
    op.drop_index('ix_timetable_entries_user', table_name='timetable_entries', schema='student')
    op.drop_table('timetable_entries', schema='student')
