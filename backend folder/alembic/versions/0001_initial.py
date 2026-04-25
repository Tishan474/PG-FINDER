"""Initial schema with PostGIS

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import geoalchemy2

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "owner", "admin", name="userrole"),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("uq_users_email", "users", ["email"], unique=True)

    op.create_table(
        "amenities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_amenities"),
        sa.UniqueConstraint("name", name="uq_amenities_name"),
    )
    op.create_index("ix_amenities_id", "amenities", ["id"])

    op.create_table(
        "pg_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("area", sa.String(200), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.Geography(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "gender_type",
            sa.Enum("boys", "girls", "co-ed", name="gendertype"),
            nullable=False,
        ),
        sa.Column("rating", sa.Numeric(3, 2), nullable=False, server_default="0"),
        sa.Column("total_reviews", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"],
            name="fk_pg_listings_created_by_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_pg_listings"),
    )
    op.create_index("ix_pg_listings_id", "pg_listings", ["id"])
    op.create_index("ix_pg_listings_name", "pg_listings", ["name"])
    op.create_index("ix_pg_listings_area", "pg_listings", ["area"])
    op.create_index("ix_pg_listings_city", "pg_listings", ["city"])
    op.create_index("ix_pg_listings_price", "pg_listings", ["price"])
    op.create_index("ix_pg_listings_gender_type", "pg_listings", ["gender_type"])
    op.create_index("ix_pg_listings_created_by", "pg_listings", ["created_by"])
    op.create_index("ix_pg_listings_price_gender", "pg_listings", ["price", "gender_type"])
    op.create_index("ix_pg_listings_city_area", "pg_listings", ["city", "area"])
    op.execute(
        "CREATE INDEX ix_pg_listings_location_gist ON pg_listings USING GIST (location)"
    )

    op.create_table(
        "pg_amenities",
        sa.Column("pg_id", sa.Integer(), nullable=False),
        sa.Column("amenity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["pg_id"], ["pg_listings.id"],
            name="fk_pg_amenities_pg_id_pg_listings",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["amenity_id"], ["amenities.id"],
            name="fk_pg_amenities_amenity_id_amenities",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("pg_id", "amenity_id", name="pk_pg_amenities"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pg_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Numeric(3, 1), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name="fk_reviews_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["pg_id"], ["pg_listings.id"],
            name="fk_reviews_pg_id_pg_listings",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        sa.PrimaryKeyConstraint("id", name="pk_reviews"),
    )
    op.create_index("ix_reviews_id", "reviews", ["id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])
    op.create_index("ix_reviews_pg_id", "reviews", ["pg_id"])

    op.create_table(
        "saved_pgs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pg_id", sa.Integer(), nullable=False),
        sa.Column(
            "saved_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name="fk_saved_pgs_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["pg_id"], ["pg_listings.id"],
            name="fk_saved_pgs_pg_id_pg_listings",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", "pg_id", name="uq_saved_pgs_user_id_pg_id"),
        sa.PrimaryKeyConstraint("id", name="pk_saved_pgs"),
    )
    op.create_index("ix_saved_pgs_id", "saved_pgs", ["id"])
    op.create_index("ix_saved_pgs_user_id", "saved_pgs", ["user_id"])
    op.create_index("ix_saved_pgs_pg_id", "saved_pgs", ["pg_id"])


def downgrade() -> None:
    op.drop_table("saved_pgs")
    op.drop_table("reviews")
    op.drop_table("pg_amenities")
    op.drop_table("pg_listings")
    op.drop_table("amenities")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS gendertype")
    op.execute("DROP TYPE IF EXISTS userrole")
