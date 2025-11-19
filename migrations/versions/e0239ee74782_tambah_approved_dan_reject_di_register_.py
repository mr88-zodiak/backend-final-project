"""tambah_approved_dan_reject_di_register_login

Revision ID: e0239ee74782
Revises: 1fa65a38a233
Create Date: 2025-10-02 18:13:59.443907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0239ee74782'
down_revision = '1fa65a38a233'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'register_login',
        'status',
        server_default=sa.text("'pending'"),
        existing_type=sa.Enum('rejected', 'approved', 'pending', name='permission_enum'),
        existing_nullable=False
    )

def downgrade():
    op.alter_column(
        'register_login',
        'status',
        server_default=sa.text("'approved'"),
        existing_type=sa.Enum('rejected', 'approved', name='permission_enum'),
        existing_nullable=False
    )