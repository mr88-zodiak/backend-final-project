"""hapus table admin dan donatur, kemudian ubah table penerima jadi register_login

Revision ID: 933e323d8099
Revises: b51fba2f511b
Create Date: 2025-09-25 12:34:59.759076
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '933e323d8099'
down_revision = 'b51fba2f511b'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    # 1. Buat tabel register_login jika belum ada
    if 'register_login' not in existing_tables:
        op.create_table(
            'register_login',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=120), nullable=False, unique=True),
            sa.Column('username', sa.String(length=80), nullable=False, unique=True),
            sa.Column('password', sa.String(length=200), nullable=False),
            sa.Column('role', sa.Enum('admin', 'donatur', 'penerima', name='role_enum'), nullable=False, server_default='admin'),
            sa.Column('login_stamp', sa.DateTime(), nullable=True),
            sa.Column('register_stamp', sa.DateTime(), nullable=True),
            sa.Column('pasif_deleter', sa.Boolean(), nullable=True)
        )

    # 2. Pindahkan data lama ke register_login
    if 'penerima' in existing_tables:
        op.execute("""
            INSERT INTO register_login(id, name, email, username, password, role, login_stamp, register_stamp, pasif_deleter)
            SELECT id, name, email, username, password, 'penerima', login_stamp, register_stamp, pasif_deleter
            FROM penerima
        """)

    if 'donatur' in existing_tables:
        op.execute("""
            INSERT INTO register_login(id, name, email, username, password, role, login_stamp, register_stamp, pasif_deleter)
            SELECT id, name, email, username, password, 'donatur', login_stamp, register_stamp, pasif_delete
            FROM donatur
        """)

    # 3. Buat foreign key ke tabel lain
    fk_map = {
        'barang': [('id_donatur', 'register_login', 'id')],
        'data_diri_penerima': [('id_penerima', 'register_login', 'id')],
        'donasi': [('id_penerima', 'register_login', 'id'), ('id_donatur', 'register_login', 'id')],
        'hasil_klasifikasi': [('id_penerima', 'register_login', 'id')],
        'hasil_rekomendasi': [('id_penerima', 'register_login', 'id')]
    }

    for table, fks in fk_map.items():
        if table in existing_tables:
            with op.batch_alter_table(table) as batch_op:
                for col, ref_table, ref_col in fks:
                    batch_op.create_foreign_key(
                        f"{table}_{col}_fkey", ref_table, [col], [ref_col], ondelete='CASCADE'
                    )

    # 4. Drop tabel lama
    for t in ['penerima', 'donatur', 'admin']:
        if t in existing_tables:
            op.drop_table(t)



def downgrade():
    # ### 1. Re-create tabel lama ###
    op.create_table('admin',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(80), nullable=False, unique=True),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('login_stamp', sa.DateTime(), nullable=True)
    )

    op.create_table('donatur',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
        sa.Column('username', sa.String(80), nullable=False, unique=True),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('login_stamp', sa.DateTime(), nullable=True),
        sa.Column('register_stamp', sa.DateTime(), nullable=True),
        sa.Column('pasif_delete', sa.Boolean(), nullable=True)
    )

    op.create_table('penerima',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
        sa.Column('username', sa.String(80), nullable=False, unique=True),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('login_stamp', sa.DateTime(), nullable=True),
        sa.Column('register_stamp', sa.DateTime(), nullable=True),
        sa.Column('pasif_deleter', sa.Boolean(), nullable=True)
    )

    # ### 2. Drop foreign key dulu sebelum drop tabel register_login ###
    tables_with_fk = ['barang', 'data_diri_penerima', 'donasi', 'hasil_klasifikasi', 'hasil_rekomendasi']
    for t in tables_with_fk:
        with op.batch_alter_table(t, schema=None) as batch_op:
            batch_op.drop_constraint(None, type_='foreignkey')

    # ### 3. Drop tabel register_login ###
    op.drop_table('register_login')
