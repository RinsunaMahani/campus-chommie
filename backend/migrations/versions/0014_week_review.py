"""The week in review's alert.

Revision ID: 0014_week_review
Revises: 0013_money_checkin
Create Date: 2026-10-25

No new table: the review is worked out on each request from what the app already holds. Written by hand, because
autogenerate doesn't compare CHECK constraints: the alerts table's kinds gain "review.ready" and its links gain
"review", and the switches' topics gain "week_review". A downgrade deletes those alerts and switches first, so the
old checks fit again.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0014_week_review'
down_revision = '0013_money_checkin'
branch_labels = None
depends_on = None

ACCOUNT_KINDS = ["account.locked", "account.new_phone", "account.password_changed", "account.phones_signed_out"]
CLASS_KINDS = ["class.event_cancelled", "class.event_changed", "class.event_moved", "class.event_new"]
FUNDING_KINDS = ["funding.closing", "funding.open"]
REVIEW_KINDS = ["review.ready"]


def _listed(values):
    return ", ".join(f"'{v}'" for v in values)


def _checks(kinds, link_types, topics):
    op.drop_constraint('ck_notifications_kind', 'notifications', schema='platform', type_='check')
    op.drop_constraint('ck_notifications_link_type', 'notifications', schema='platform', type_='check')
    op.drop_constraint('ck_notification_switches_topic', 'notification_switches', schema='platform', type_='check')
    op.create_check_constraint('ck_notifications_kind', 'notifications', f"kind IN ({_listed(sorted(kinds))})",
                               schema='platform')
    op.create_check_constraint('ck_notifications_link_type', 'notifications',
                               f"link_type IS NULL OR link_type IN ({_listed(link_types)})", schema='platform')
    op.create_check_constraint('ck_notification_switches_topic', 'notification_switches',
                               f"topic IN ({_listed(sorted(topics))})", schema='platform')


def upgrade():
    _checks(ACCOUNT_KINDS + CLASS_KINDS + FUNDING_KINDS + REVIEW_KINDS, ["security", "class", "funding", "review"],
            ["class_updates", "funding_reminders", "week_review"])


def downgrade():
    op.execute(f"DELETE FROM platform.notifications WHERE kind IN ({_listed(REVIEW_KINDS)}) OR link_type = 'review'")
    op.execute("DELETE FROM platform.notification_switches WHERE topic = 'week_review'")
    _checks(ACCOUNT_KINDS + CLASS_KINDS + FUNDING_KINDS, ["security", "class", "funding"],
            ["class_updates", "funding_reminders"])
