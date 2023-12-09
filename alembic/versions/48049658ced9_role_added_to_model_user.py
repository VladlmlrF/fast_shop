"""role added to model User

Revision ID: 48049658ced9
Revises: 7310d57d37a8
Create Date: 2023-12-09 21:12:27.854277

"""
from typing import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "48049658ced9"
down_revision: Union[str, None] = "7310d57d37a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("role", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "role")
    # ### end Alembic commands ###
