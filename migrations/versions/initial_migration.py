"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-02-xx
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Используем server_default для created_at
    op.add_column('users', sa.Column('assistant_thread_id', sa.String(), nullable=True))
    op.add_column('users', 
                  sa.Column('created_at', 
                           sa.DateTime(), 
                           nullable=False,
                           server_default=sa.text('NOW()')))

def downgrade() -> None:
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'assistant_thread_id') 