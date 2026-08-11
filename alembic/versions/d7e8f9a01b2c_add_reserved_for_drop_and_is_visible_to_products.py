"""add_reserved_for_drop_and_is_visible_to_products

Revision ID: d7e8f9a01b2c
Revises: ceff8b624bdb
Create Date: 2026-08-11 21:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7e8f9a01b2c'
down_revision: Union[str, Sequence[str], None] = 'ceff8b624bdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('products', sa.Column('is_reserved_for_drop', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('products', sa.Column('is_visible', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('products', 'is_visible')
    op.drop_column('products', 'is_reserved_for_drop')
