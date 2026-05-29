"""create todos table

Revision ID: 08d939e4c525
Revises: c6f96693df36
Create Date: 2026-05-29 10:52:51.609449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08d939e4c525'
down_revision: Union[str, Sequence[str], None] = 'c6f96693df36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
