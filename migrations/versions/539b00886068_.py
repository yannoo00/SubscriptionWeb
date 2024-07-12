"""empty message

Revision ID: 539b00886068
Revises: 89b671c25e75
Create Date: 2024-07-12 11:06:33.872722

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '539b00886068'
down_revision = '89b671c25e75'
branch_labels = None
depends_on = None

def upgrade():
    # chat_room 테이블 삭제
    op.drop_table('chat_room')

    # 새로운 구조로 chat_room 테이블 재생성
    op.create_table('chat_room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id'], name='fk_chat_room_creator')
    )

def downgrade():
    op.drop_table('chat_room')
    op.create_table('chat_room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )