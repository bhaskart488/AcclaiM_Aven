"""Add completion status to AdRequest

Revision ID: 058a29600a53
Revises: 
Create Date: 2024-08-10 00:22:10.008946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '058a29600a53'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completion_status', sa.String(length=20), nullable=False, server_default='Incomplete'))

def downgrade():
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.drop_column('completion_status')

def upgrade():
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completion_status', sa.String(length=20), nullable=False, server_default='Incomplete'))

def downgrade():
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.drop_column('completion_status')