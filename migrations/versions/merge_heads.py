"""merge heads

Revision ID: merge_heads_xxx
Revises: ID1, ID2  # Здесь будут реальные ID из команды history
Create Date: 2024-02-xx
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'merge_heads_xxx'
down_revision = ('ID1', 'ID2')  # Те же ID, что и выше
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем таблицу users, если её нет
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('assistant_thread_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )

def downgrade() -> None:
    op.drop_table('users') 