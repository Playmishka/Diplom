"""empty message

Revision ID: 2f0e91478334
Revises: deb7194c7eb3
Create Date: 2024-04-12 13:28:54.715253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f0e91478334'
down_revision: Union[str, None] = 'deb7194c7eb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_per_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('product', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product'], ['product.id'], ),
    sa.ForeignKeyConstraint(['request_id'], ['request.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('prodcut_per_request')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prodcut_per_request',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('request_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['product'], ['product.id'], name='prodcut_per_request_product_fkey'),
    sa.ForeignKeyConstraint(['request_id'], ['request.id'], name='prodcut_per_request_request_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='prodcut_per_request_pkey')
    )
    op.drop_table('product_per_request')
    # ### end Alembic commands ###