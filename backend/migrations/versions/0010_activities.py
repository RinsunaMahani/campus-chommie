"""A student's own activities.

Revision ID: 0010_activities
Revises: 0009_money_goals
Create Date: 2026-10-21

student.activities holds what a student adds to their own week besides classes: a name, a broad kind, every week
on a weekday or once on a date, a start and end time, and optionally where. Nothing about them. A row goes with its
account (ON DELETE CASCADE). Written by hand to match the model, with its CHECK constraints.
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0010_activities'
down_revision = '0009_money_goals'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('activities',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=60), nullable=False),
    sa.Column('kind', sa.String(length=12), nullable=False),
    sa.Column('weekday', sa.SmallInteger(), nullable=True),
    sa.Column('on_date', sa.Date(), nullable=True),
    sa.Column('starts_at', sa.Time(), nullable=False),
    sa.Column('ends_at', sa.Time(), nullable=False),
    sa.Column('place', sa.String(length=80), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('(weekday IS NULL) <> (on_date IS NULL)', name='ck_activities_one_schedule'),
    sa.CheckConstraint('weekday IS NULL OR weekday BETWEEN 0 AND 6', name='ck_activities_weekday'),
    sa.CheckConstraint('ends_at > starts_at', name='ck_activities_order'),
    sa.CheckConstraint("kind IN ('personal', 'social', 'errands', 'exercise', 'work', 'other')", name='ck_activities_kind'),
    sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='student'
    )
    op.create_index('ix_activities_user', 'activities', ['user_id', 'weekday', 'on_date'], unique=False, schema='student')


def downgrade():
    op.drop_index('ix_activities_user', table_name='activities', schema='student')
    op.drop_table('activities', schema='student')
