from sqlalchemy import text

TRIGGERS = [
    # Country
    text("""
    CREATE OR REPLACE FUNCTION move_to_country_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO country_deleted (country_id, flag_id, deleted_at)
        VALUES (OLD.country_id, OLD.flag_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_country_deleted
    BEFORE DELETE ON country
    FOR EACH ROW EXECUTE FUNCTION move_to_country_deleted();
    """),
    # CountryTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_country_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO country_translate_deleted (country_id, language_id, name, deleted_at)
        VALUES (OLD.country_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_country_translate_deleted
    BEFORE DELETE ON country_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_country_translate_deleted();
    """),
    # Region
    text("""
    CREATE OR REPLACE FUNCTION move_to_region_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO region_deleted (region_id, country_id, deleted_at)
        VALUES (OLD.region_id, OLD.country_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_region_deleted
    BEFORE DELETE ON region
    FOR EACH ROW EXECUTE FUNCTION move_to_region_deleted();
    """),
    # RegionTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_region_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO region_translate_deleted (region_id, language_id, name, deleted_at)
        VALUES (OLD.region_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_region_translate_deleted
    BEFORE DELETE ON region_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_region_translate_deleted();
    """),
    # Grape
    text("""
    CREATE OR REPLACE FUNCTION move_to_grape_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO grape_deleted (grape_id, region_id, deleted_at)
        VALUES (OLD.grape_id, OLD.region_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_grape_deleted
    BEFORE DELETE ON grape
    FOR EACH ROW EXECUTE FUNCTION move_to_grape_deleted();
    """),
    # GrapeTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_grape_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO grape_translate_deleted (grape_id, language_id, name, deleted_at)
        VALUES (OLD.grape_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_grape_translate_deleted
    BEFORE DELETE ON grape_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_grape_translate_deleted();
    """),
    # Product
    text("""
    CREATE OR REPLACE FUNCTION move_to_product_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO product_deleted (product_id, price, discount, main_image_link, video_link, presentation_type_id, deleted_at)
        VALUES (OLD.product_id, OLD.price, OLD.discount, OLD.main_image_link, OLD.video_link, OLD.presentation_type_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_product_deleted
    BEFORE DELETE ON product
    FOR EACH ROW EXECUTE FUNCTION move_to_product_deleted();
    """),
    # ProductTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_product_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO product_translate_deleted (product_id, language_id, name, deleted_at)
        VALUES (OLD.product_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_product_translate_deleted
    BEFORE DELETE ON product_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_product_translate_deleted();
    """),
    # WineCategory
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_category_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO wine_category_deleted (wine_category_id, deleted_at)
        VALUES (OLD.wine_category_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_category_deleted
    BEFORE DELETE ON wine_category
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_category_deleted();
    """),
    # WineCategoryTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_category_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO wine_category_translate_deleted (wine_category_id, language_id, name, deleted_at)
        VALUES (OLD.wine_category_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_category_translate_deleted
    BEFORE DELETE ON wine_category_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_category_translate_deleted();
    """),
    # WineType
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_type_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO wine_type_deleted (wine_type_id, deleted_at)
        VALUES (OLD.wine_type_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_type_deleted
    BEFORE DELETE ON wine_type
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_type_deleted();
    """),
    # WineTypeTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_type_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO wine_type_translate_deleted (wine_type_id, language_id, name, deleted_at)
        VALUES (OLD.wine_type_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_type_translate_deleted
    BEFORE DELETE ON wine_type_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_type_translate_deleted();
    """),
    # Aroma
    text("""
    CREATE OR REPLACE FUNCTION move_to_aroma_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO aroma_deleted (aroma_id, deleted_at)
        VALUES (OLD.aroma_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_aroma_deleted
    BEFORE DELETE ON aroma
    FOR EACH ROW EXECUTE FUNCTION move_to_aroma_deleted();
    """),
    # AromaTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_aroma_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO aroma_translate_deleted (aroma_id, language_id, name, deleted_at)
        VALUES (OLD.aroma_id, OLD.language_id, OLD.name, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_aroma_translate_deleted
    BEFORE DELETE ON aroma_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_aroma_translate_deleted();
    """),
    # Sort
    text("""
    CREATE OR REPLACE FUNCTION move_to_sort_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO sort_deleted (grape_id, product_id, percentage_content, deleted_at)
        VALUES (OLD.grape_id, OLD.product_id, OLD.percentage_content, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_sort_deleted
    BEFORE DELETE ON sort
    FOR EACH ROW EXECUTE FUNCTION move_to_sort_deleted();
    """),
    # Wine
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO wine_deleted (product_id, volume, wine_strength, harvest_year, wine_type_id, wine_category_id, min_serving_temperature, max_serving_temperature, deleted_at)
        VALUES (OLD.product_id, OLD.volume, OLD.wine_strength, OLD.harvest_year, OLD.wine_type_id, OLD.wine_category_id, OLD.min_serving_temperature, OLD.max_serving_temperature, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_deleted
    BEFORE DELETE ON wine
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_deleted();
    """),
    # WineTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_translate_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO wine_translate_deleted (wine_id, language_id, production_method_description, description, deleted_at)
        VALUES (OLD.wine_id, OLD.language_id, OLD.production_method_description, OLD.description, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_translate_deleted
    BEFORE DELETE ON wine_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_translate_deleted();
    """),
    # AromaWine
    text("""
    CREATE OR REPLACE FUNCTION move_to_aroma_wine_deleted()
    RETURNS TRIGGER AS $
    BEGIN
        INSERT INTO aroma_wine_deleted (product_id, aroma_id, deleted_at)
        VALUES (OLD.product_id, OLD.aroma_id, NOW());
        RETURN OLD;
    END;
    $ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_aroma_wine_deleted
    BEFORE DELETE ON aroma_wine
    FOR EACH ROW EXECUTE FUNCTION move_to_aroma_wine_deleted();
    """),
]
