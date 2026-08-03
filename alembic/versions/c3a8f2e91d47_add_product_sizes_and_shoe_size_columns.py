"""add product sizes and shoe size columns

Revision ID: c3a8f2e91d47
Revises: 02e80a1a09bf
Create Date: 2026-08-03 16:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a8f2e91d47'
down_revision: Union[str, Sequence[str], None] = '02e80a1a09bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create product_sizes table
    op.create_table('product_sizes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('size', sa.String(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'size', name='unique_product_size')
    )
    op.create_index(op.f('ix_product_sizes_id'), 'product_sizes', ['id'], unique=False)

    # 2. Add size column to cart_items
    op.add_column('cart_items', sa.Column('size', sa.String(), nullable=False, server_default='US 9'))

    # 3. Drop old unique constraint and create new one including size
    op.drop_constraint('unique_user_product', 'cart_items', type_='unique')
    op.create_unique_constraint('unique_user_product_size', 'cart_items', ['user_id', 'product_id', 'size'])

    # 4. Add size column to entries
    op.add_column('entries', sa.Column('size', sa.String(), nullable=False, server_default='US 9'))

    # 5. Add size column to order_items
    op.add_column('order_items', sa.Column('size', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # 5. Remove size from order_items
    op.drop_column('order_items', 'size')

    # 4. Remove size from entries
    op.drop_column('entries', 'size')

    # 3. Drop new constraint and restore old one
    op.drop_constraint('unique_user_product_size', 'cart_items', type_='unique')
    op.create_unique_constraint('unique_user_product', 'cart_items', ['user_id', 'product_id'])

    # 2. Remove size from cart_items
    op.drop_column('cart_items', 'size')

    # 1. Drop product_sizes table
    op.drop_index(op.f('ix_product_sizes_id'), table_name='product_sizes')
    op.drop_table('product_sizes')
