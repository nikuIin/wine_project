import decimal
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import (
    TEXT,
    UUID,
    VARCHAR,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import MONEY, NUMERIC, TIMESTAMP, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.types import DATE, SMALLINT
from uuid_extensions import uuid7

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
        ForeignKey("flag.flag_id", ondelete="CASCADE"),
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
    author_translates = relationship("Author", back_populates="language")
    city_translates = relationship("CityTranslate", back_populates="language")
    blog_category_translates = relationship(
        "BlogCategoryTranslate", back_populates="language"
    )
    tag_translates = relationship("TagTranslate", back_populates="language")
    article_translates = relationship(
        "ArticleTranslate", back_populates="language"
    )
    status_translate = relationship(
        "StatusTranslate", back_populates="language"
    )


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
    permissions = relationship(
        "Permission", secondary="role_permission", back_populates="roles"
    )


class User(Base, TimeStampMixin):
    __tablename__ = "user"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        nullable=False,
    )
    login: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    email: Mapped[str | None] = mapped_column(
        VARCHAR(320),
        nullable=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("role.role_id", ondelete="CASCADE"),
        nullable=False,
    )
    is_registered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(login) > 0", name="user_login_check"),
        CheckConstraint("length(password) > 0", name="user_password_check"),
        CheckConstraint("length(email) >= 3", name="user_email_check"),
    )

    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    md_user = relationship("MdUser", back_populates="user", uselist=False)
    author_translates = relationship("Author", back_populates="user")
    social_networks = relationship(
        "SocialNetwork",
        secondary="user_social_network",
        back_populates="users",
    )
    articles = relationship("Article", back_populates="author")


class Permission(Base):
    __tablename__ = "permission"

    permission_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="permission_name_check"),
    )

    roles = relationship(
        "Role", secondary="role_permission", back_populates="permissions"
    )


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("role.role_id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("permission.permission_id", ondelete="CASCADE"),
        primary_key=True,
    )


class Author(Base):
    __tablename__ = "author"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    work_place: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    post: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    awards: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    biography: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    experience: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    education: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "length(work_place) > 0", name="author_work_place_check"
        ),
        CheckConstraint("length(post) > 0", name="author_post_check"),
    )

    user = relationship("User", back_populates="author_translates")
    language = relationship("Language", back_populates="author_translates")


class City(Base):
    __tablename__ = "city"

    city_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("region.region_id", ondelete="CASCADE"),
        nullable=False,
    )

    region = relationship("Region", back_populates="cities")
    city_translates = relationship("CityTranslate", back_populates="city")


class CityTranslate(Base):
    __tablename__ = "city_translate"

    city_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("city.city_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="city_name_check"),
    )

    city = relationship("City", back_populates="city_translates")
    language = relationship("Language", back_populates="city_translates")


class MdUser(Base):
    __tablename__ = "md_user"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True)
    profile_picture_link: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "length(first_name) > 0", name="md_user_first_name_check"
        ),
        CheckConstraint(
            "length(last_name) > 0", name="md_user_last_name_check"
        ),
        CheckConstraint(
            "length(middle_name) > 0", name="md_user_middle_name_check"
        ),
        CheckConstraint(
            "length(profile_picture_link) > 0",
            name="md_user_profile_picture_link_check",
        ),
    )

    user = relationship("User", back_populates="md_user")


class SocialNetwork(Base):
    __tablename__ = "social_network"

    social_network_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    link: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    image_src: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="social_network_name_check"),
        CheckConstraint("length(link) > 0", name="social_network_link_check"),
        CheckConstraint(
            "length(image_src) > 0", name="social_network_image_src_check"
        ),
    )

    users = relationship(
        "User",
        secondary="user_social_network",
        back_populates="social_networks",
    )


class UserSocialNetwork(Base):
    __tablename__ = "user_social_network"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    social_network_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("social_network.social_network_id", ondelete="CASCADE"),
        primary_key=True,
    )


class BlogCategory(Base):
    __tablename__ = "blog_category"

    blog_category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    image_src: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("blog_category.blog_category_id", ondelete="CASCADE"),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint("length(slug) > 0", name="blog_category_slug_check"),
    )

    parent = relationship("BlogCategory", remote_side=[blog_category_id])
    blog_category_translates = relationship(
        "BlogCategoryTranslate", back_populates="blog_category"
    )
    article = relationship("Article", back_populates="blog_category")


class BlogCategoryTranslate(Base):
    __tablename__ = "blog_category_translate"

    blog_category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("blog_category.blog_category_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="blog_category_name_check"),
        CheckConstraint(
            "length(description) > 0", name="blog_category_description_check"
        ),
    )

    blog_category = relationship(
        "BlogCategory", back_populates="blog_category_translates"
    )
    language = relationship(
        "Language", back_populates="blog_category_translates"
    )


class Tag(Base):
    __tablename__ = "tag"

    tag_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tag_translates = relationship("TagTranslate", back_populates="tag")
    tag_article = relationship("TagArticle", back_populates="tag")


class TagTranslate(Base):
    __tablename__ = "tag_translate"

    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tag.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="tag_name_check"),
        UniqueConstraint(
            "name", "language_id", name="tag_name_language_unique"
        ),
    )

    tag = relationship("Tag", back_populates="tag_translates")
    language = relationship("Language", back_populates="tag_translates")


class TagArticle(Base, TimeStampMixin):
    __tablename__ = "tag_article"

    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tag.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("article.article_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    article = relationship("Article", back_populates="tag_article")
    tag = relationship("Tag", back_populates="tag_article")


class Article(Base, TimeStampMixin):
    __tablename__ = "article"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        nullable=False,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("blog_category.blog_category_id", ondelete="CASCADE"),
        nullable=True,
    )
    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("status.status_id", ondelete="CASCADE"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    __table_args__ = (
        CheckConstraint("views_count >= 0", name="article_views_count_check"),
    )

    author = relationship("User", back_populates="articles")
    article_translates = relationship(
        "ArticleTranslate", back_populates="article"
    )
    blog_category = relationship("BlogCategory", back_populates="article")
    status = relationship("Status", back_populates="article")
    tag_article = relationship("TagArticle", back_populates="article")


class ArticleTranslate(Base):
    __tablename__ = "article_translate"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("article.article_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    image_src: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    tsv_content: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="article_title_check"),
        CheckConstraint("length(content) >= 0", name="article_content_check"),
        UniqueConstraint(
            "title", "language_id", name="article_title_language_unique"
        ),
    )

    article = relationship("Article", back_populates="article_translates")
    language = relationship("Language", back_populates="article_translates")


class RefreshToken(Base, TimeStampMixin):
    __tablename__ = "refresh_token"

    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
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
        ForeignKey("refresh_token.refresh_token_id", ondelete="CASCADE"),
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
        ForeignKey("flag.flag_id", ondelete="CASCADE"),
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
        ForeignKey("country.country_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "language_id",
            "name",
        ),
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
    cities = relationship("City", back_populates="region")


class RegionTranslate(Base):
    __tablename__ = "region_translate"

    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("region.region_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "language_id",
            "name",
        ),
    )
    region = relationship("Region", back_populates="region_translates")
    language = relationship("Language", back_populates="region_translates")


class Grape(Base, TimeStampMixin):
    __tablename__ = "grape"

    grape_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("region.region_id", ondelete="CASCADE"),
        nullable=False,
    )

    region = relationship("Region", back_populates="grapes")
    sorts = relationship("Sort", back_populates="grape")
    grape_translates = relationship("GrapeTranslate", back_populates="grape")


class GrapeTranslate(Base):
    __tablename__ = "grape_translate"

    grape_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grape.grape_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
        default=uuid7,
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
        ForeignKey(
            "presentation_type.presentation_type_id", ondelete="CASCADE"
        ),
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
        ForeignKey("product.product_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
        ForeignKey("wine_category.wine_category_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
        ForeignKey("wine_type.wine_type_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
        ForeignKey("aroma.aroma_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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

    grape_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grape.grape_id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wine.product_id", ondelete="CASCADE"),
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
        ForeignKey("product.product_id", ondelete="CASCADE"),
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
        ForeignKey("wine_type.wine_type_id", ondelete="CASCADE"),
        nullable=False,
    )
    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wine_category.wine_category_id", ondelete="CASCADE"),
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
        ForeignKey("wine.product_id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
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
        ForeignKey("wine.product_id", ondelete="CASCADE"),
        primary_key=True,
    )
    aroma_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("aroma.aroma_id", ondelete="CASCADE"),
        primary_key=True,
    )

    wine = relationship("Wine", back_populates="aroma_wines")
    aroma = relationship("Aroma", back_populates="aroma_wines")


class Status(Base):
    __tablename__ = "status"

    status_id: Mapped[Integer] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    status_translate = relationship("StatusTranslate", back_populates="status")
    article = relationship("Article", back_populates="status")


class StatusTranslate(Base):
    __tablename__ = "status_translate"
    __table_args__ = (
        CheckConstraint("length(name) > 0", name="check_name_len"),
    )

    status_id: Mapped[Integer] = mapped_column(
        Integer,
        ForeignKey("status.status_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[VARCHAR] = mapped_column(
        VARCHAR(255),
        nullable=False,
    )
    language_id: Mapped[VARCHAR] = mapped_column(
        VARCHAR(10),
        ForeignKey("language.language_id", ondelete="CASCADE"),
        nullable=False,
    )

    language = relationship("Language", back_populates="status_translate")
    status = relationship("Status", back_populates="status_translate")


class CountryDeleted(Base):
    __tablename__ = "country_deleted"

    country_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    flag_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class CountryTranslateDeleted(Base):
    __tablename__ = "country_translate_deleted"

    country_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class RegionDeleted(Base):
    __tablename__ = "region_deleted"

    region_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    country_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class RegionTranslateDeleted(Base):
    __tablename__ = "region_translate_deleted"

    region_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class GrapeDeleted(Base, TimeStampMixin):
    __tablename__ = "grape_deleted"

    grape_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    region_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class GrapeTranslateDeleted(Base):
    __tablename__ = "grape_translate_deleted"

    grape_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class ProductDeleted(Base):
    __tablename__ = "product_deleted"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
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
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class ProductTranslateDeleted(Base):
    __tablename__ = "product_translate_deleted"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class WineCategoryDeleted(Base):
    __tablename__ = "wine_category_deleted"

    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class WineCategoryTranslateDeleted(Base):
    __tablename__ = "wine_category_translate_deleted"

    wine_category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class WineTypeDeleted(Base):
    __tablename__ = "wine_type_deleted"

    wine_type_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class WineTypeTranslateDeleted(Base):
    __tablename__ = "wine_type_translate_deleted"

    wine_type_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class AromaDeleted(Base):
    __tablename__ = "aroma_deleted"

    aroma_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class AromaTranslateDeleted(Base):
    __tablename__ = "aroma_translate_deleted"

    aroma_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class SortDeleted(Base):
    __tablename__ = "sort_deleted"

    grape_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    percentage_content: Mapped[decimal.Decimal] = mapped_column(
        NUMERIC(5, 2),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class WineDeleted(Base, TimeStampMixin):
    __tablename__ = "wine_deleted"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
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
        nullable=False,
    )
    wine_category_id: Mapped[int] = mapped_column(
        Integer,
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
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class WineTranslateDeleted(Base):
    __tablename__ = "wine_translate_deleted"

    wine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
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
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class UserDeleted(Base):
    __tablename__ = "user_deleted"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    login: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    is_registered: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class MdUserDeleted(Base):
    __tablename__ = "md_user_deleted"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    middle_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    profile_picture_link: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class AromaWineDeleted(Base):
    __tablename__ = "aroma_wine_deleted"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    aroma_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )


class ArticleDeleted(Base, TimeStampMixin):
    __tablename__ = "article_deleted"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )

    __table_args__ = (
        CheckConstraint("views_count >= 0", name="article_views_count_check"),
    )


class ArticleTranslateDeleted(Base):
    __tablename__ = "article_translate_deleted"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    language_id: Mapped[str] = mapped_column(
        VARCHAR(10),
        primary_key=True,
    )
    image_src: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    tsv_content: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now,
    )

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="article_title_check"),
    )
