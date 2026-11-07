
"""change embedding dimension to 384

Revision ID: 4653080f819e
Revises: 4215867be6c7
"""

from typing import Sequence, Union

from alembic import op


revision: str = "4653080f819e"
down_revision: Union[str, Sequence[str], None] = "4215867be6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE page_chunks
        ALTER COLUMN embedding TYPE vector(384)
        USING NULL::vector(384);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE page_chunks
        ALTER COLUMN embedding TYPE vector(1536)
        USING NULL::vector(1536);
        """
    )
