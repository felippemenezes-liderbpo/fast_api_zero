"""add updated_at column in users table

Revision ID: 04442b8651ca
Revises: 9adc2c83f08c
Create Date: 2026-01-04 17:41:27.369583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04442b8651ca'
down_revision: Union[str, Sequence[str], None] = '9adc2c83f08c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'updated_at')
