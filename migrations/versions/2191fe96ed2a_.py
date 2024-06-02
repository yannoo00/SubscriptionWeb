"""empty message

Revision ID: 2191fe96ed2a
Revises: 572ff573de57
Create Date: 2024-05-29 14:43:21.592576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2191fe96ed2a'
down_revision = '572ff573de57'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.drop_column('file')

    # ### end Alembic commands ###
