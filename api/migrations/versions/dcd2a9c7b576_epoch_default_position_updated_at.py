"""epoch default position_updated_at

Revision ID: dcd2a9c7b576
Revises: 16d20a8d1c5f
Create Date: 2026-10-03 13:40:46.406138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcd2a9c7b576'
down_revision = '16d20a8d1c5f'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('tracks', schema=None) as batch_op:
        batch_op.alter_column(
            'position_updated_at',
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            nullable=True,
            server_default=None,
        )

    op.execute(
        "UPDATE tracks SET position_updated_at = NULL "
        "WHERE id NOT IN (SELECT track_id FROM track_progress)"
    )


def downgrade():
    op.execute(
        "UPDATE tracks SET position_updated_at = CURRENT_TIMESTAMP "
        "WHERE position_updated_at IS NULL"
    )

    with op.batch_alter_table('tracks', schema=None) as batch_op:
        batch_op.alter_column(
            'position_updated_at',
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
            nullable=False,
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
        )
