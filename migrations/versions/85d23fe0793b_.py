"""empty message

Revision ID: 85d23fe0793b
Revises: edaf1d8c7b0a
Create Date: 2024-07-10 10:23:07.932383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85d23fe0793b'
down_revision = 'edaf1d8c7b0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_progress', schema=None) as batch_op:
        batch_op.drop_column('image')

    # ### end Alembic commands ###
