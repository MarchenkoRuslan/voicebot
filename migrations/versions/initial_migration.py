"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-02-xx
"""
from alembic import op
import sqlalchemy as sa

revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Удаляем старую таблицу
    op.drop_table('users')
    
    # Создаем новую таблицу со всеми полями
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('assistant_thread_id', sa.String(), nullable=True),
        sa.Column('values', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )

def downgrade() -> None:
    op.drop_table('users') 