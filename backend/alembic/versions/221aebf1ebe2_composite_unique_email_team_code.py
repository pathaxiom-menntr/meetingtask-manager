"""composite_unique_email_team_code

Revision ID: 221aebf1ebe2
Revises: ce8a5d5dfc0b
Create Date: 2026-07-02 11:49:30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '221aebf1ebe2'
down_revision: Union[str, Sequence[str], None] = 'ce8a5d5dfc0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop the old single-column unique constraint on users.email and replace it
    with a composite unique constraint on (email, team_code).
    This allows the same email address to belong to multiple teams.
    """
    # Drop the old unique constraint on email alone
    op.drop_constraint('users_email_key', 'users', type_='unique')

    # Add composite unique constraint on (email, team_code)
    op.create_unique_constraint(
        'uq_users_email_team_code',
        'users',
        ['email', 'team_code']
    )


def downgrade() -> None:
    """Reverse: restore single-column unique on email, drop composite."""
    op.drop_constraint('uq_users_email_team_code', 'users', type_='unique')
    op.create_unique_constraint('users_email_key', 'users', ['email'])
