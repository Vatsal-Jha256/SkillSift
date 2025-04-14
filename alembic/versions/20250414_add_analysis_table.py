"""add analysis table

Revision ID: 20250414_add_analysis_table
Create Date: 2025-04-14 23:55:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '20250414_add_analysis_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Use batch_alter_table to handle SQLite limitations
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'analysis' not in tables:
        # Create table if it doesn't exist
        op.create_table(
            'analysis',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('resume_filename', sa.String()),
            sa.Column('analysis_data', sqlite.JSON().with_variant(sa.JSON(), 'postgresql'), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )
        op.create_index(op.f('ix_analysis_id'), 'analysis', ['id'], unique=True)
    else:
        # Table exists, check and add missing columns
        columns = [col['name'] for col in inspector.get_columns('analysis')]
        with op.batch_alter_table('analysis') as batch_op:
            if 'analysis_data' not in columns:
                batch_op.add_column(sa.Column(
                    'analysis_data',
                    sqlite.JSON().with_variant(sa.JSON(), 'postgresql'),
                    nullable=False,
                    server_default='{}'
                ))

def downgrade():
    op.drop_index(op.f('ix_analysis_id'), table_name='analysis')
    op.drop_table('analysis')