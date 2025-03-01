"""merge heads

Revision ID: merge_heads
Revises: # укажите здесь ID всех существующих миграций через запятую
Create Date: 2024-02-xx
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = 'merge_heads'
# Укажите здесь ID всех существующих миграций в кортеже
down_revision = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

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