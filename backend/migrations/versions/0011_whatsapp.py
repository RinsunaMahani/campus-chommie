"""The WhatsApp bot (M6): linked numbers, link codes, messages seen.

Revision ID: 0011_whatsapp
Revises: 0010_activities
Create Date: 2026-10-23

classes.whatsapp_links keeps a linked number only as a keyed hash (64 hex
characters), one account per number; classes.whatsapp_link_codes the one-time
code an account is linking with, hashed the same way; both go with their
account (ON DELETE CASCADE). classes.whatsapp_seen holds hashes of message ids
Meta sent in the last 48 hours, so a retry is answered once; no person in it.
Written by hand (`flask db check` finds nothing missing); the CHECK constraints
are spelled out because autogenerate doesn't compare them.
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0011_whatsapp'
down_revision = '0010_activities'
branch_labels = None
depends_on = None

HEX64 = "~ '^[0-9a-f]{64}$'"


def _base():
    return [
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    ]


def upgrade():
    op.create_table('whatsapp_links',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('phone_hash', sa.String(length=64), nullable=False),
    *_base(),
    sa.CheckConstraint(f"phone_hash {HEX64}", name='ck_whatsapp_links_phone_hash'),
    sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
    sa.UniqueConstraint('phone_hash', name='uq_whatsapp_links_phone'),
    schema='classes'
    )
    op.create_index('ix_whatsapp_links_user', 'whatsapp_links', ['user_id'], unique=False, schema='classes')

    op.create_table('whatsapp_link_codes',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('code_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    *_base(),
    sa.CheckConstraint(f"code_hash {HEX64}", name='ck_whatsapp_link_codes_code_hash'),
    sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], ondelete='CASCADE'),
    sa.UniqueConstraint('user_id', name='uq_whatsapp_link_codes_user'),
    sa.UniqueConstraint('code_hash', name='uq_whatsapp_link_codes_code'),
    schema='classes'
    )

    op.create_table('whatsapp_seen',
    sa.Column('message_hash', sa.String(length=64), nullable=False),
    *_base(),
    sa.CheckConstraint(f"message_hash {HEX64}", name='ck_whatsapp_seen_message_hash'),
    sa.UniqueConstraint('message_hash', name='uq_whatsapp_seen_message'),
    schema='classes'
    )
    op.create_index('ix_whatsapp_seen_created', 'whatsapp_seen', ['created_at'], unique=False, schema='classes')


def downgrade():
    op.drop_index('ix_whatsapp_seen_created', table_name='whatsapp_seen', schema='classes')
    op.drop_table('whatsapp_seen', schema='classes')
    op.drop_table('whatsapp_link_codes', schema='classes')
    op.drop_index('ix_whatsapp_links_user', table_name='whatsapp_links', schema='classes')
    op.drop_table('whatsapp_links', schema='classes')
