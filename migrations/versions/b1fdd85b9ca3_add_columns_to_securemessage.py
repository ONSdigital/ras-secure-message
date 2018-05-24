"""add columns to securemessage

Revision ID: b1fdd85b9ca3
Revises:
Create Date: 2018-05-24 14:46:04.172799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1fdd85b9ca3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('secure_message', sa.Column('sent_datetime', sa.DateTime), schema='securemessage')
    op.add_column('secure_message', sa.Column('read_datetime', sa.DateTime), schema='securemessage')


def downgrade():
    op.drop_column('secure_message', 'sent_datetime')
    op.drop_column('secure_message', 'read_datetime')
