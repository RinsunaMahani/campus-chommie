"""Money pots (Family, Stokvel, Buffer, Big purchase).

Revision ID: 0011_money_pots
Revises: 0010_activities
Create Date: 2026-10-22

Extends student.money_goals to support named pots:
- kind: 'goal' (default), 'family', 'stokvel', 'buffer', 'big_purchase'.
- family and stokvel: monthly amounts with no date (due_on is null).
- buffer: target emergency buffer with no date (due_on is null).
- big_purchase: target amount, due_on date, plus stokvel_funded boolean.
Check constraints enforce valid kind values and due_on presence rules.
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0011_money_pots'
down_revision = '0010_activities'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'money_goals',
        sa.Column('kind', sa.String(length=16), nullable=False, server_default='goal'),
        schema='student',
    )
    op.add_column(
        'money_goals',
        sa.Column('stokvel_funded', sa.Boolean(), nullable=False, server_default=sa.false()),
        schema='student',
    )
    op.alter_column(
        'money_goals',
        'due_on',
        existing_type=sa.Date(),
        nullable=True,
        schema='student',
    )
    op.create_check_constraint(
        'ck_money_goals_kind',
        'money_goals',
        "kind IN ('goal', 'family', 'stokvel', 'buffer', 'big_purchase')",
        schema='student',
    )
    op.create_check_constraint(
        'ck_money_goals_due_on',
        'money_goals',
        "(kind IN ('goal', 'big_purchase') AND due_on IS NOT NULL) OR "
        "(kind IN ('family', 'stokvel', 'buffer') AND due_on IS NULL)",
        schema='student',
    )


def downgrade():
    op.drop_constraint('ck_money_goals_due_on', 'money_goals', schema='student', type_='check')
    op.drop_constraint('ck_money_goals_kind', 'money_goals', schema='student', type_='check')
    op.execute("UPDATE student.money_goals SET due_on = CURRENT_DATE WHERE due_on IS NULL")
    op.alter_column(
        'money_goals',
        'due_on',
        existing_type=sa.Date(),
        nullable=False,
        schema='student',
    )
    op.drop_column('money_goals', 'stokvel_funded', schema='student')
    op.drop_column('money_goals', 'kind', schema='student')

