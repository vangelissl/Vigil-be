"""update_analyses_table_classification_result_type_to_json

Revision ID: f6c02fa590ad
Revises: ca7a19fb46d5
Create Date: 2026-06-01 10:39:50.545666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6c02fa590ad'
down_revision: Union[str, Sequence[str], None] = 'ca7a19fb46d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('analyses', 'classification_result')
    op.add_column('analyses', sa.Column('classification_result', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('analyses', 'classification_result')
    op.add_column('analyses', sa.Column('classification_result', sa.DOUBLE_PRECISION(precision=53), nullable=True))
