# models.py
import decimal
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import (
    UUID,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import MONEY, NUMERIC, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DATE, SMALLINT, TEXT, VARCHAR

from core.config import auth_settings
from db.base_models import Base, TimeStampMixin


class Language(Base):
    __tablename__ = "language"

    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    flag_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("flag.flag_id"),
        nullable=True,
    )

    flag = relationship("Flag", back_populates="languages")
    country_translates = relationship(
        "CountryTranslate", back_populates="language"
    )
    region_translates = relationship(
        "RegionTranslate", back_populates="language"
    )
    grape_translates = relationship(
        "GrapeTranslate", back_populates="language"
    )
    product_translates = relationship(
        "ProductTranslate", back_populates="language"
    )
    wine_category_translates = relationship(
        "WineCategoryTranslate", back_populates="language"
    )
    wine_type_translates = relationship(
        "WineTypeTranslate", back_populates="language"
    )
    aroma_translates = relationship(
        "AromaTranslate", back_populates="language"
    )
    wine_translates = relationship("WineTranslate", back_populates="language")


class Flag(Base):
    __tablename__ = "flag"

    flag_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    flag_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    languages = relationship("Language", back_populates="flag")
    countries = relationship("Country", back_populates="flag")


class Role(Base):
    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="role_name_check"),
    )

    users = relationship("User", back_populates="role")


class User(Base, TimeStampMixin):
    __tablename__ = "user"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    login: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("role.role_id"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(login) > 0", name="user_login_check"),
        CheckConstraint("length(password) > 0", name="user_password_check"),
    )

    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base, TimeStampMixin):
    __tablename__ = "refresh_token"

    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id"),
        nullable=False,
    )
    expire_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: (
            datetime.now()
            + timedelta(minutes=auth_settings.refresh_token_expire_minutes)
        ),
    )

    user = relationship("User", back_populates="refresh_tokens")
    blacklisted = relationship(
        "BlackRefreshTokenList",
        back_populates="refresh_token",
        uselist=False,
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
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )

    refresh_token = relationship("RefreshToken", back_populates="blacklisted")


class PresentationType(Base):
    __tablename__ = "presentation_type"

    presentation_type_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    products = relationship("Product", back_populates="presentation_type")


class Country(Base):
    __tablename__ = "country"

    country_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    flag_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("flag.flag_id"),
        nullable=True,
    )

    flag = relationship("Flag", back_populates="countries")
    regions = relationship("Region", back_populates="country")
    country_translates = relationship(
        "CountryTranslate", back_populates="country"
    )


class CountryTranslate(Base):
    __tablename__ = "country_translate"

    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("country.country_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    country = relationship("Country", back_populates="country_translates")
    language = relationship("Language", back_populates="country_translates")


class Region(Base):
    __tablename__ = "region"

    region_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("country.country_id", ondelete="CASCADE"),
        nullable=False,
    )

    country = relationship("Country", back_populates="regions")
    grapes = relationship("Grape", back_populates="region")
    region_translates = relationship(
        "RegionTranslate", back_populates="region"
    )


class RegionTranslate(Base):
    __tablename__ = "region_translate"

    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("region.region_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    region = relationship("Region", back_populates="region_translates")
    language = relationship("Language", back_populates="region_translates")


class Grape(Base, TimeStampMixin):
    __tablename__ = "grape"

    grape_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("region.region_id"),
        nullable=False,
    )

    region = relationship("Region", back_populates="grapes")
    sorts = relationship("Sort", back_populates="grape")
    grape_translates = relationship("GrapeTranslate", back_populates="grape")


class GrapeTranslate(Base):
    __tablename__ = "grape_translate"

    grape_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grape.grape_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    grape = relationship("Grape", back_populates="grape_translates")
    language = relationship("Language", back_populates="grape_translates")


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        CheckConstraint("price::numeric >= 0", name="check_price_positive"),
        CheckConstraint("discount >= 0", name="check_discount_positive"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    price: Mapped[decimal.Decimal] = mapped_column(
        MONEY,
        nullable=False,
    )
    discount: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(3, 2),
        default=0,
        nullable=False,
    )
    main_image_link: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    video_link: Mapped[str | None] = mapped_column(
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
    product_translates = relationship(
        "ProductTranslate", back_populates="product"
    )


class ProductTranslate(Base):
    __tablename__ = "product_translate"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product.product_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    product = relationship("Product", back_populates="product_translates")
    language = relationship("Language", back_populates="product_translates")


class WineCategory(Base):
    __tablename__ = "wine_category"

    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    wine = relationship("Wine", back_populates="wine_category")
    wine_category_translates = relationship(
        "WineCategoryTranslate", back_populates="wine_category"
    )


class WineCategoryTranslate(Base):
    __tablename__ = "wine_category_translate"

    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wine_category.wine_category_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    wine_category = relationship(
        "WineCategory", back_populates="wine_category_translates"
    )
    language = relationship(
        "Language", back_populates="wine_category_translates"
    )


class WineType(Base):
    __tablename__ = "wine_type"

    wine_type_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    wine = relationship("Wine", back_populates="wine_type")
    wine_type_translates = relationship(
        "WineTypeTranslate", back_populates="wine_type"
    )


class WineTypeTranslate(Base):
    __tablename__ = "wine_type_translate"

    wine_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wine_type.wine_type_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    wine_type = relationship("WineType", back_populates="wine_type_translates")
    language = relationship("Language", back_populates="wine_type_translates")


class Aroma(Base):
    __tablename__ = "aroma"

    aroma_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    aroma_wines = relationship("AromaWine", back_populates="aroma")
    aroma_translates = relationship("AromaTranslate", back_populates="aroma")


class AromaTranslate(Base):
    __tablename__ = "aroma_translate"

    aroma_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("aroma.aroma_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    aroma = relationship("Aroma", back_populates="aroma_translates")
    language = relationship("Language", back_populates="aroma_translates")


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
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wine.product_id"),
        primary_key=True,
    )
    percentage_content: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(5, 2),
        nullable=False,
    )

    grape = relationship("Grape", back_populates="sorts")
    wine = relationship("Wine", back_populates="sorts")


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

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product.product_id"),
        primary_key=True,
    )
    volume: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(4, 2),
        nullable=False,
    )
    wine_strength: Mapped[decimal.Decimal | None] = mapped_column(
        NUMERIC(5, 2),
        nullable=True,
    )
    harvest_year: Mapped[date] = mapped_column(
        DATE,
        nullable=False,
    )
    wine_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wine_type.wine_type_id"),
        nullable=False,
    )
    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wine_category.wine_category_id"),
        nullable=False,
    )
    min_serving_temperature: Mapped[int | None] = mapped_column(
        SMALLINT,
        nullable=True,
    )
    max_serving_temperature: Mapped[int | None] = mapped_column(
        SMALLINT,
        nullable=True,
    )

    product = relationship("Product", back_populates="wine")
    wine_type = relationship("WineType", back_populates="wine")
    wine_category = relationship("WineCategory", back_populates="wine")
    aroma_wines = relationship("AromaWine", back_populates="wine")
    sorts = relationship("Sort", back_populates="wine")
    wine_translates = relationship("WineTranslate", back_populates="wine")


class WineTranslate(Base):
    __tablename__ = "wine_translate"

    wine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wine.product_id"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id"),
        primary_key=True,
    )
    production_method_description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    wine = relationship("Wine", back_populates="wine_translates")
    language = relationship("Language", back_populates="wine_translates")


class AromaWine(Base):
    __tablename__ = "aroma_wine"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wine.product_id"),
        primary_key=True,
    )
    aroma_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("aroma.aroma_id"),
        primary_key=True,
    )

    wine = relationship("Wine", back_populates="aroma_wines")
    aroma = relationship("Aroma", back_populates="aroma_wines")
