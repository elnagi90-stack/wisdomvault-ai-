"""empty message

Revision ID: 6b9d98898bed
Revises: f406a1d7cc08
Create Date: 2026-08-16 01:48:53.272211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b9d98898bed'
down_revision: Union[str, Sequence[str], None] = 'f406a1d7cc08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
