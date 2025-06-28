import decimal
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import UUID, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import MONEY, NUMERIC, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DATE, SMALLINT, TEXT

from core.config import auth_settings
from db.base_models import Base, TimeStampMixin


class Role(Base):
    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="role_name_check"),
    )


class User(Base, TimeStampMixin):
    __tablename__ = "user"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    login: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("role.role_id"), nullable=False
    )

    __table_args__ = (
        CheckConstraint("length(login) > 0", name="user_login_check"),
        CheckConstraint("length(password) > 0", name="user_password_check"),
    )


class RefreshToken(Base, TimeStampMixin):
    __tablename__ = "refresh_token"

    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
    )
    expire_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: (
            datetime.now()
            + timedelta(minutes=auth_settings.refresh_token_expire_minutes)
        ),
    )


class BlackRefreshTokenList(Base):
    __tablename__ = "black_refresh_token_list"

    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("refresh_token.refresh_token_id"),
        primary_key=True,
        nullable=False,
    )
    ban_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )


# Reference schema
class PresentationType(Base):
    __tablename__ = "presentation_type"

    presentation_type_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    products = relationship("Product", back_populates="presentation_type")


# Grape schema
class Country(Base):
    __tablename__ = "country"

    country_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    flag_url: Mapped[str] = mapped_column(
        String(256),
        comment="The url to the country flag image",
        nullable=True,
    )

    regions = relationship("Region", back_populates="country")


class Region(Base):
    __tablename__ = "region"

    region_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("country.country_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    country = relationship("Country", back_populates="regions")
    grapes = relationship("Grape", back_populates="region")


class Grape(Base, TimeStampMixin):
    __tablename__ = "grape"

    grape_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("region.region_id"),
        nullable=False,
    )

    region = relationship("Region", back_populates="grapes")
    sorts = relationship("Sort", back_populates="grape")


# Catalog schema
class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        CheckConstraint("price::numeric >= 0", name="check_price_positive"),
        CheckConstraint("discount >= 0", name="check_discount_positive"),
    )

    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    price: Mapped[float] = mapped_column(
        MONEY,
        nullable=False,
    )
    discount: Mapped[float] = mapped_column(
        NUMERIC(3, 2),
        default=0,
        nullable=False,
    )
    main_image_link: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    video_link: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    presentation_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("presentation_type.presentation_type_id"),
        nullable=False,
    )

    presentation_type = relationship(
        "PresentationType", back_populates="products"
    )
    wine = relationship("Wine", back_populates="product", uselist=False)
    sorts = relationship("Sort", back_populates="product")


class WineCategory(Base):
    __tablename__ = "wine_category"

    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )


class WineType(Base):
    __tablename__ = "wine_type"

    wine_type_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )


class Aroma(Base):
    __tablename__ = "aroma"

    aroma_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    wines = relationship("AromaWine", back_populates="aroma")


class Sort(Base):
    __tablename__ = "sort"
    __table_args__ = (
        CheckConstraint(
            "percentage_content > 0", name="check_percentage_content_positive"
        ),
    )

    grape_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grape.grape_id"),
        primary_key=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product.product_id"),
        primary_key=True,
    )
    percentage_content: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(5, 2),
        nullable=False,
    )

    grape = relationship("Grape", back_populates="sorts")
    product = relationship("Product", back_populates="sorts")


class Wine(Base, TimeStampMixin):
    __tablename__ = "wine"
    __table_args__ = (
        CheckConstraint("volume > 0", name="check_volume_positive"),
        CheckConstraint(
            "wine_strength >= 0", name="check_wine_strength_non_negative"
        ),
        CheckConstraint(
            "harvest_year >= '1900-01-01' AND harvest_year <= CURRENT_DATE",
            name="check_harvest_year",
        ),
    )

    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product.product_id"),
        primary_key=True,
    )
    volume: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(4, 2),
        nullable=False,
    )
    wine_strength: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(5, 2),
        nullable=True,
    )
    harvest_year: Mapped[date] = mapped_column(
        DATE,
        nullable=False,
    )
    production_method_description: Mapped[str] = mapped_column(
        TEXT,
        nullable=True,
    )
    taste_description: Mapped[str] = mapped_column(
        TEXT,
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        TEXT,
        nullable=True,
    )
    min_serving_temperature: Mapped[int] = mapped_column(
        SMALLINT,
        nullable=True,
    )
    max_serving_temperature: Mapped[int] = mapped_column(
        SMALLINT,
        nullable=True,
    )

    product = relationship("Product", back_populates="wine")
    aromas = relationship("AromaWine", back_populates="wine")


class AromaWine(Base):
    __tablename__ = "aroma_wine"

    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wine.product_id"),
        primary_key=True,
    )
    aroma_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("aroma.aroma_id"),
        primary_key=True,
    )

    wine = relationship("Wine", back_populates="aromas")
    aroma = relationship("Aroma", back_populates="wines")
