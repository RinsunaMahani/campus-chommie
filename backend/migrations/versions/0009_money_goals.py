"""Money goals.

Revision ID: 0009_money_goals
Revises: 0008_exams
Create Date: 2026-10-21

student.money_goals holds what a student is putting money aside for: a label, the amount, how much is already
aside, the date, and whether the date came from their university's fee dates (the amount always comes from the
student). Nothing about them. A row goes with its account (ON DELETE CASCADE). Written by hand to match the
model, with its CHECK constraints.
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0009_money_goals'
down_revision = '0008_exams'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('money_goals',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('label', sa.String(length=80), nullable=False),
    sa.Column('amount_cents', sa.BigInteger(), nullable=False),
    sa.Column('saved_cents', sa.BigInteger(), nullable=False),
    sa.Column('due_on', sa.Date(), nullable=False),
    sa.Column('from_university', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('amount_cents > 0', name='ck_money_goals_amount'),
    sa.CheckConstraint('saved_cents >= 0', name='ck_money_goals_saved'),
    sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='student'
    )
    op.create_index('ix_money_goals_user', 'money_goals', ['user_id', 'due_on'], unique=False, schema='student')


def downgrade():
    op.drop_index('ix_money_goals_user', table_name='money_goals', schema='student')
    op.drop_table('money_goals', schema='student')
