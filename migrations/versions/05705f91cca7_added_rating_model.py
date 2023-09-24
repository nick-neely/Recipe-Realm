"""Added rating model

Revision ID: 05705f91cca7
Revises: 7ce63db30e98
Create Date: 2023-09-23 17:35:37.792576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05705f91cca7'
down_revision = '7ce63db30e98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('profile_picture',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=20),
               existing_nullable=False,
               existing_server_default=sa.text("'default.jpg'"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('profile_picture',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=120),
               existing_nullable=False,
               existing_server_default=sa.text("'default.jpg'"))

    op.drop_table('rating')
    # ### end Alembic commands ###