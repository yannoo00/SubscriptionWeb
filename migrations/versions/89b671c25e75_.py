"""empty message

Revision ID: 89b671c25e75
Revises: 96568fc4e865
Create Date: 2024-07-10 11:14:12.524674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89b671c25e75'
down_revision = '96568fc4e865'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ai_conversation_link', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('ai_conversation_file', sa.String(length=255), nullable=True))
        batch_op.drop_column('ai_conversation')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ai_conversation', sa.TEXT(), nullable=True))
        batch_op.drop_column('ai_conversation_file')
        batch_op.drop_column('ai_conversation_link')

    # ### end Alembic commands ###
