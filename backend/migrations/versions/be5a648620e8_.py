"""empty message

Revision ID: be5a648620e8
Revises: 
Create Date: 2022-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Explicitly set the revision variable
revision = 'be5a648620e8'
down_revision = None

# Create the 'roles' table
def upgrade():
    # Drop the 'roles' table if it exists
    op.drop_table('roles')

    # Create the 'roles' table
    op.create_table('roles',
                    sa.Column('id', sa.VARCHAR(length=11), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )

    # Add the 'role_id' column to the 'users' table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.String(length=11), nullable=True))


    # Create a foreign key constraint on the 'users' table
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])

# Drop the 'roles' table and its associated foreign key constraint
def downgrade():
    # Drop the foreign key constraint on the 'users' table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_role_id', type_='foreignkey')

    # Drop the 'roles' table
    op.drop_table('roles')
