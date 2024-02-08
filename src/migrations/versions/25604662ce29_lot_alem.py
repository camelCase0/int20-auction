"""Lot alem

Revision ID: 25604662ce29
Revises: c33327aa50dd
Create Date: 2024-02-06 13:48:43.706069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25604662ce29'
down_revision: Union[str, None] = 'c33327aa50dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bet',
    sa.Column('bet_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('bet_id')
    )
    op.create_table('lot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_bet', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lot')
    op.drop_table('bet')
    # ### end Alembic commands ###