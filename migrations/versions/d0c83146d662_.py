"""empty message

Revision ID: d0c83146d662
Revises: 4af610e73b45
Create Date: 2022-01-03 23:54:02.868330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0c83146d662'
down_revision = '4af610e73b45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scenic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('star', sa.Integer(), nullable=True),
    sa.Column('logo', sa.String(length=255), nullable=True),
    sa.Column('introduction', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('is_hot', sa.Boolean(), nullable=True),
    sa.Column('is_recommended', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('logo'),
    sa.UniqueConstraint('title')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('pwd', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=11), nullable=True),
    sa.Column('info', sa.Text(), nullable=True),
    sa.Column('face', sa.String(length=255), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('face'),
    sa.UniqueConstraint('phone')
    )
    op.create_index(op.f('ix_user_addtime'), 'user', ['addtime'], unique=False)
    op.create_table('collect',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scenic_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['scenic_id'], ['scenic.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collect_addtime'), 'collect', ['addtime'], unique=False)
    op.create_table('userlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('ip', sa.String(length=100), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_userlog_addtime'), 'userlog', ['addtime'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_userlog_addtime'), table_name='userlog')
    op.drop_table('userlog')
    op.drop_index(op.f('ix_collect_addtime'), table_name='collect')
    op.drop_table('collect')
    op.drop_index(op.f('ix_user_addtime'), table_name='user')
    op.drop_table('user')
    op.drop_table('scenic')
    # ### end Alembic commands ###
