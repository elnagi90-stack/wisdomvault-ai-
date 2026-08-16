"""merge core and ai migration heads

Revision ID: f406a1d7cc08
Revises: 6626622043ae
Create Date: 2026-08-15 21:48:57.154485

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f406a1d7cc08"
down_revision: Union[str, Sequence[str], None] = "6626622043ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration branches."""
    pass


def downgrade() -> None:
    """Merge migration branches."""
    pass
