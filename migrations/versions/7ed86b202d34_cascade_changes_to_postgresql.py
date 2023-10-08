"""Cascade changes to PostgreSQL

Revision ID: 7ed86b202d34
Revises: 824e3d79a8a0
Create Date: 2023-10-07 17:42:36.518366

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData, Table



# revision identifiers, used by Alembic.
revision = '7ed86b202d34'
down_revision = '824e3d79a8a0'
branch_labels = None
depends_on = None


def upgrade():
    # Get the current bind (database connection)
    conn = op.get_bind()
    
    # If the current database is PostgreSQL
    if conn.dialect.name == 'postgresql':

        # Get the metadata
        meta = MetaData()

        rating = Table('rating', meta, autoload=True)
        
        # Drop and recreate the FK with cascade
        with op.batch_alter_table('rating') as batch_op:
            batch_op.drop_constraint('rating_recipe_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('rating_recipe_id_fkey', 'recipe', ['recipe_id'], ['id'], ondelete='CASCADE')
            batch_op.drop_constraint('rating_user_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('rating_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')

        # Comment Table
        comment = Table('comment', meta, autoload=True)
        with op.batch_alter_table('comment') as batch_op:
            batch_op.drop_constraint('comment_recipe_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('comment_recipe_id_fkey', 'recipe', ['recipe_id'], ['id'], ondelete='CASCADE')
            batch_op.drop_constraint('comment_user_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('comment_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')

        # Recipe Table
        recipe = Table('recipe', meta, autoload=True)
        with op.batch_alter_table('recipe') as batch_op:
            batch_op.drop_constraint('recipe_author_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('recipe_author_id_fkey', 'user', ['author_id'], ['id'], ondelete='CASCADE')

def downgrade():
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        
        # Get the metadata
        meta = MetaData()

        # Rating Table
        rating = Table('rating', meta, autoload=True)
        with op.batch_alter_table('rating') as batch_op:
            batch_op.drop_constraint('rating_recipe_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('rating_recipe_id_fkey', 'recipe', ['recipe_id'], ['id'])
            batch_op.drop_constraint('rating_user_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('rating_user_id_fkey', 'user', ['user_id'], ['id'])

        # Comment Table
        comment = Table('comment', meta, autoload=True)
        with op.batch_alter_table('comment') as batch_op:
            batch_op.drop_constraint('comment_recipe_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('comment_recipe_id_fkey', 'recipe', ['recipe_id'], ['id'])
            batch_op.drop_constraint('comment_user_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('comment_user_id_fkey', 'user', ['user_id'], ['id'])

        # Recipe Table
        recipe = Table('recipe', meta, autoload=True)
        with op.batch_alter_table('recipe') as batch_op:
            batch_op.drop_constraint('recipe_author_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key('recipe_author_id_fkey', 'user', ['author_id'], ['id'])