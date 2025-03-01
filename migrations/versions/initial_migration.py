"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-02-xx
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Удаляем существующую таблицу, если она есть
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    
    # Создаем таблицу заново
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), unique=True),
        sa.Column('assistant_thread_id', sa.String()),
        sa.Column('values', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, 
                  default=datetime.utcnow, onupdate=datetime.utcnow)
    )

def downgrade() -> None:
    op.drop_table('users') 