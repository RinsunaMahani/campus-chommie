"""Weekly money check-in and fixed costs.

Revision ID: 0013_money_checkin
Revises: 0012_money_pots
Create Date: 2026-10-23

Adds:
- student.fixed_costs: recurring fixed costs paid on a set day each month (rent, transport, data, phone).
- student.weekly_checkins: weekly check-in records (total spending or skip record), with the days each one filled
  in for the student (`filled`), so sending a week again never touches what the student logged themselves.
- student.money_settings.checkin_day: preferred day of the week for weekly check-in.
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0013_money_checkin'
down_revision = '0012_money_pots'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fixed_costs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('label', sa.String(length=60), nullable=False),
        sa.Column('amount_cents', sa.BigInteger(), nullable=False),
        sa.Column('day_of_month', sa.SmallInteger(), nullable=False),
        sa.CheckConstraint('amount_cents > 0', name='ck_fixed_costs_amount'),
        sa.CheckConstraint('day_of_month BETWEEN 1 AND 31', name='ck_fixed_costs_day'),
        sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='student',
    )
    op.create_index('ix_fixed_costs_user', 'fixed_costs', ['user_id'], unique=False, schema='student')

    op.create_table(
        'weekly_checkins',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('week_end', sa.Date(), nullable=False),
        sa.Column('amount_cents', sa.BigInteger(), nullable=True),
        sa.Column('skipped', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('filled', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint(
            '((skipped = TRUE AND amount_cents IS NULL) OR (skipped = FALSE AND amount_cents IS NOT NULL AND amount_cents >= 0))',
            name='ck_weekly_checkins_state',
        ),
        sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'week_end', name='uq_weekly_checkins_user_week'),
        schema='student',
    )

    op.add_column(
        'money_settings',
        sa.Column('checkin_day', sa.String(length=10), nullable=False, server_default='sunday'),
        schema='student',
    )
    op.create_check_constraint(
        'ck_money_settings_checkin_day',
        'money_settings',
        "checkin_day IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')",
        schema='student',
    )


def downgrade():
    op.drop_constraint('ck_money_settings_checkin_day', 'money_settings', schema='student', type_='check')
    op.drop_column('money_settings', 'checkin_day', schema='student')
    op.drop_table('weekly_checkins', schema='student')
    op.drop_index('ix_fixed_costs_user', table_name='fixed_costs', schema='student')
    op.drop_table('fixed_costs', schema='student')

