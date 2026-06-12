"""Add firm tenant scope

Revision ID: 2f6a41d9b9c3
Revises: 928b1ba0be93
Create Date: 2026-06-12 10:00:00.000000

"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "2f6a41d9b9c3"
down_revision = "928b1ba0be93"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "firms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("firm_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_users_firm_id_firms",
            "firms",
            ["firm_id"],
            ["id"]
        )

    with op.batch_alter_table("clients") as batch_op:
        batch_op.add_column(sa.Column("firm_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_clients_firm_id_firms",
            "firms",
            ["firm_id"],
            ["id"]
        )

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.add_column(sa.Column("firm_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_audit_logs_firm_id_firms",
            "firms",
            ["firm_id"],
            ["id"]
        )

    firms = sa.table(
        "firms",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("created_at", sa.DateTime),
    )
    op.bulk_insert(
        firms,
        [
            {
                "id": 1,
                "name": "Default Firm",
                "created_at": datetime.now(timezone.utc),
            }
        ]
    )

    op.execute("UPDATE users SET firm_id = 1 WHERE firm_id IS NULL")
    op.execute("UPDATE clients SET firm_id = 1 WHERE firm_id IS NULL")
    op.execute("UPDATE audit_logs SET firm_id = 1 WHERE firm_id IS NULL")

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("firm_id", existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table("clients") as batch_op:
        batch_op.alter_column("firm_id", existing_type=sa.Integer(), nullable=False)


def downgrade():
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_constraint("fk_audit_logs_firm_id_firms", type_="foreignkey")
        batch_op.drop_column("firm_id")

    with op.batch_alter_table("clients") as batch_op:
        batch_op.drop_constraint("fk_clients_firm_id_firms", type_="foreignkey")
        batch_op.drop_column("firm_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("fk_users_firm_id_firms", type_="foreignkey")
        batch_op.drop_column("firm_id")

    op.drop_table("firms")
