"""refactor model Order

Revision ID: 8dfe1c9b4332
Revises: f4b7e3ba9ef6
Create Date: 2023-12-13 23:45:59.081317

"""
from typing import Sequence
from typing import Union

from alembic import op

# import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8dfe1c9b4332"
down_revision: Union[str, None] = "f4b7e3ba9ef6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, "orders", "users", ["user_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "orders", type_="foreignkey")
    # ### end Alembic commands ###
