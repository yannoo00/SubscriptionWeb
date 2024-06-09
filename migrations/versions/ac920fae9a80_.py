"""empty message

Revision ID: ac920fae9a80
Revises: ad8513ea1ef1
Create Date: 2024-06-04 16:54:26.640207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac920fae9a80'
down_revision = 'ad8513ea1ef1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_participant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hours_contributed', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_participant', schema=None) as batch_op:
        batch_op.drop_column('hours_contributed')

    # ### end Alembic commands ###
