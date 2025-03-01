"""add assistant_thread_id

Revision ID: xxx
Revises: # предыдущий ID или пусто, если это первая миграция
Create Date: 2024-02-xx

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'xxx'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('assistant_thread_id', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'assistant_thread_id') 