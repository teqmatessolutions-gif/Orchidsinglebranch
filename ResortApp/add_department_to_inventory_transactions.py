"""add department to inventory transactions

Revision ID: add_dept_to_inv_trans
Revises: 
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_dept_to_inv_trans'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add department column to inventory_transactions table
    op.add_column('inventory_transactions', 
                  sa.Column('department', sa.String(), nullable=True))


def downgrade():
    # Remove department column from inventory_transactions table
    op.drop_column('inventory_transactions', 'department')
