"""empty message

Revision ID: e551ba596dcf
Revises: 2488d7e0ffd8
Create Date: 2025-06-28 04:48:48.310552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e551ba596dcf'
down_revision: Union[str, Sequence[str], None] = '2488d7e0ffd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('AdminUser', schema=None) as batch_op:
        batch_op.alter_column('banned_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('AdminUser', schema=None) as batch_op:
        batch_op.alter_column('banned_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

    # ### end Alembic commands ###
