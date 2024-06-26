"""empty message

Revision ID: 5a3b9173fd69
Revises: ac920fae9a80
Create Date: 2024-06-11 23:06:00.116779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a3b9173fd69'
down_revision = 'ac920fae9a80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_participant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accepted', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_participant', schema=None) as batch_op:
        batch_op.drop_column('accepted')

    # ### end Alembic commands ###