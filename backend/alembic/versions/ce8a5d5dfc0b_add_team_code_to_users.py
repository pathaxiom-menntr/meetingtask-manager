"""add_team_code_to_users

Revision ID: ce8a5d5dfc0b
Revises: cb5cf058762f
Create Date: 2026-07-02 11:06:21.334492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce8a5d5dfc0b'
down_revision: Union[str, Sequence[str], None] = 'cb5cf058762f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add team_code column with a safe default so existing rows are backfilled
    op.add_column(
        'users',
        sa.Column('team_code', sa.String(length=50), server_default='default', nullable=False)
    )
    op.create_index(op.f('ix_users_team_code'), 'users', ['team_code'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_team_code'), table_name='users')
    op.drop_column('users', 'team_code')
