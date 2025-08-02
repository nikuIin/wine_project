from sqlalchemy import text

TRIGGERS = [
    # Country
    text("""
    CREATE OR REPLACE FUNCTION move_to_country_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO country_deleted (country_id, flag_id, deleted_at)
        VALUES (OLD.country_id, OLD.flag_id, NOW())
        ON CONFLICT (country_id) DO UPDATE SET flag_id = EXCLUDED.flag_id, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_country_deleted
    BEFORE DELETE ON country
    FOR EACH ROW EXECUTE FUNCTION move_to_country_deleted();
    """),
    # CountryTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_country_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO country_translate_deleted (country_id, language_id, name, deleted_at)
        VALUES (OLD.country_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (country_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_country_translate_deleted
    BEFORE DELETE ON country_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_country_translate_deleted();
    """),
    # Region
    text("""
    CREATE OR REPLACE FUNCTION move_to_region_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO region_deleted (region_id, country_id, deleted_at)
        VALUES (OLD.region_id, OLD.country_id, NOW())
        ON CONFLICT (region_id) DO UPDATE SET country_id = EXCLUDED.country_id, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_region_deleted
    BEFORE DELETE ON region
    FOR EACH ROW EXECUTE FUNCTION move_to_region_deleted();
    """),
    # RegionTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_region_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO region_translate_deleted (region_id, language_id, name, deleted_at)
        VALUES (OLD.region_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (region_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_region_translate_deleted
    BEFORE DELETE ON region_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_region_translate_deleted();
    """),
    # Grape
    text("""
    CREATE OR REPLACE FUNCTION move_to_grape_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO grape_deleted (grape_id, region_id, deleted_at)
        VALUES (OLD.grape_id, OLD.region_id, NOW())
        ON CONFLICT (grape_id) DO UPDATE SET region_id = EXCLUDED.region_id, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_grape_deleted
    BEFORE DELETE ON grape
    FOR EACH ROW EXECUTE FUNCTION move_to_grape_deleted();
    """),
    # GrapeTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_grape_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO grape_translate_deleted (grape_id, language_id, name, deleted_at)
        VALUES (OLD.grape_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (grape_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_grape_translate_deleted
    BEFORE DELETE ON grape_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_grape_translate_deleted();
    """),
    # Product
    text("""
    CREATE OR REPLACE FUNCTION move_to_product_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO product_deleted (product_id, price, discount, main_image_link, video_link, presentation_type_id, deleted_at)
        VALUES (OLD.product_id, OLD.price, OLD.discount, OLD.main_image_link, OLD.video_link, OLD.presentation_type_id, NOW())
        ON CONFLICT (product_id) DO UPDATE SET price = EXCLUDED.price, discount = EXCLUDED.discount, main_image_link = EXCLUDED.main_image_link, video_link = EXCLUDED.video_link, presentation_type_id = EXCLUDED.presentation_type_id, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_product_deleted
    BEFORE DELETE ON product
    FOR EACH ROW EXECUTE FUNCTION move_to_product_deleted();
    """),
    # ProductTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_product_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO product_translate_deleted (product_id, language_id, name, deleted_at)
        VALUES (OLD.product_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (product_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_product_translate_deleted
    BEFORE DELETE ON product_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_product_translate_deleted();
    """),
    # WineCategory
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_category_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO wine_category_deleted (wine_category_id, deleted_at)
        VALUES (OLD.wine_category_id, NOW())
        ON CONFLICT (wine_category_id) DO UPDATE SET deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_category_deleted
    BEFORE DELETE ON wine_category
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_category_deleted();
    """),
    # WineCategoryTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_category_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO wine_category_translate_deleted (wine_category_id, language_id, name, deleted_at)
        VALUES (OLD.wine_category_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (wine_category_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_category_translate_deleted
    BEFORE DELETE ON wine_category_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_category_translate_deleted();
    """),
    # WineType
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_type_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO wine_type_deleted (wine_type_id, deleted_at)
        VALUES (OLD.wine_type_id, NOW())
        ON CONFLICT (wine_type_id) DO UPDATE SET deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_type_deleted
    BEFORE DELETE ON wine_type
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_type_deleted();
    """),
    # WineTypeTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_type_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO wine_type_translate_deleted (wine_type_id, language_id, name, deleted_at)
        VALUES (OLD.wine_type_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (wine_type_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_type_translate_deleted
    BEFORE DELETE ON wine_type_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_type_translate_deleted();
    """),
    # Aroma
    text("""
    CREATE OR REPLACE FUNCTION move_to_aroma_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO aroma_deleted (aroma_id, deleted_at)
        VALUES (OLD.aroma_id, NOW())
        ON CONFLICT (aroma_id) DO UPDATE SET deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_aroma_deleted
    BEFORE DELETE ON aroma
    FOR EACH ROW EXECUTE FUNCTION move_to_aroma_deleted();
    """),
    # AromaTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_aroma_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO aroma_translate_deleted (aroma_id, language_id, name, deleted_at)
        VALUES (OLD.aroma_id, OLD.language_id, OLD.name, NOW())
        ON CONFLICT (aroma_id, language_id) DO UPDATE SET name = EXCLUDED.name, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_aroma_translate_deleted
    BEFORE DELETE ON aroma_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_aroma_translate_deleted();
    """),
    # Sort
    text("""
    CREATE OR REPLACE FUNCTION move_to_sort_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO sort_deleted (grape_id, product_id, percentage_content, deleted_at)
        VALUES (OLD.grape_id, OLD.product_id, OLD.percentage_content, NOW())
        ON CONFLICT (grape_id, product_id) DO UPDATE SET percentage_content = EXCLUDED.percentage_content, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_sort_deleted
    BEFORE DELETE ON sort
    FOR EACH ROW EXECUTE FUNCTION move_to_sort_deleted();
    """),
    # Wine
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO wine_deleted (product_id, volume, wine_strength, harvest_year, wine_type_id, wine_category_id, min_serving_temperature, max_serving_temperature, deleted_at)
        VALUES (OLD.product_id, OLD.volume, OLD.wine_strength, OLD.harvest_year, OLD.wine_type_id, OLD.wine_category_id, OLD.min_serving_temperature, OLD.max_serving_temperature, NOW())
        ON CONFLICT (product_id) DO UPDATE SET volume = EXCLUDED.volume, wine_strength = EXCLUDED.wine_strength, harvest_year = EXCLUDED.harvest_year, wine_type_id = EXCLUDED.wine_type_id, wine_category_id = EXCLUDED.wine_category_id, min_serving_temperature = EXCLUDED.min_serving_temperature, max_serving_temperature = EXCLUDED.max_serving_temperature, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_deleted
    BEFORE DELETE ON wine
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_deleted();
    """),
    # WineTranslate
    text("""
    CREATE OR REPLACE FUNCTION move_to_wine_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO wine_translate_deleted (wine_id, language_id, production_method_description, description, deleted_at)
        VALUES (OLD.wine_id, OLD.language_id, OLD.production_method_description, OLD.description, NOW())
        ON CONFLICT (wine_id, language_id) DO UPDATE SET production_method_description = EXCLUDED.production_method_description, description = EXCLUDED.description, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_wine_translate_deleted
    BEFORE DELETE ON wine_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_wine_translate_deleted();
    """),
    # AromaWine
    text("""
    CREATE OR REPLACE FUNCTION move_to_aroma_wine_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO aroma_wine_deleted (product_id, aroma_id, deleted_at)
        VALUES (OLD.product_id, OLD.aroma_id, NOW())
        ON CONFLICT (product_id, aroma_id) DO UPDATE SET deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_aroma_wine_deleted
    BEFORE DELETE ON aroma_wine
    FOR EACH ROW EXECUTE FUNCTION move_to_aroma_wine_deleted();
    """),
    # User
    text("""
    CREATE OR REPLACE FUNCTION move_to_user_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO user_deleted (user_id, login, password, role_id, is_registered, deleted_at)
        VALUES (OLD.user_id, OLD.login, OLD.password, OLD.role_id, OLD.is_registered, NOW())
        ON CONFLICT (user_id) DO UPDATE SET login = EXCLUDED.login, password = EXCLUDED.password, role_id = EXCLUDED.role_id, is_registered = EXCLUDED.is_registered, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_user_deleted
    BEFORE DELETE ON "user"
    FOR EACH ROW EXECUTE FUNCTION move_to_user_deleted();
    """),
    # MdUser
    text("""
    CREATE OR REPLACE FUNCTION move_to_md_user_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO md_user_deleted (user_id, email, first_name, last_name, middle_name, profile_picture_link, description, deleted_at)
        VALUES (OLD.user_id, OLD.email, OLD.profile_picture_link, OLD.description, NOW())
        ON CONFLICT (user_id) DO UPDATE SET email = EXCLUDED.email, first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name, middle_name = EXCLUDED.middle_name, profile_picture_link = EXCLUDED.profile_picture_link, description = EXCLUDED.description, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_md_user_deleted
    BEFORE DELETE ON md_user
    FOR EACH ROW EXECUTE FUNCTION move_to_md_user_deleted();
    """),
    # Article
    text("""
    CREATE OR REPLACE FUNCTION move_to_article_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO article_deleted (article_id, author_id, slug, views_count, deleted_at, created_at, updated_at)
        VALUES (OLD.article_id, OLD.author_id, OLD.slug, OLD.views_count, NOW(), OLD.created_at, OLD.updated_at)
        ON CONFLICT (article_id) DO UPDATE SET author_id = EXCLUDED.author_id, slug = EXCLUDED.slug, views_count = EXCLUDED.views_count, deleted_at = NOW(), created_at = EXCLUDED.created_at, updated_at = EXCLUDED.updated_at;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_article_deleted
    BEFORE DELETE ON article
    FOR EACH ROW EXECUTE FUNCTION move_to_article_deleted();
    """),
    # Article-translate
    text("""
    CREATE OR REPLACE FUNCTION move_to_article_translate_deleted()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO article_translate_deleted (article_id, image_src, language_id, title, content, tsv_content, deleted_at)
        VALUES (OLD.article_id, OLD.image_src, OLD.language_id, OLD.title, OLD.content, OLD.tsv_content, NOW())
        ON CONFLICT (article_id, language_id) DO UPDATE SET image_src = EXCLUDED.image_src, title = EXCLUDED.title, content = EXCLUDED.content, tsv_content = EXCLUDED.tsv_content, deleted_at = NOW();
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """),
    text("""
    CREATE TRIGGER trigger_move_to_article_translate_deleted
    BEFORE DELETE ON article_translate
    FOR EACH ROW EXECUTE FUNCTION move_to_article_translate_deleted();
    """),
    # Content
    text("""create or replace function move_to_content_deleted()
    returns trigger as $$
    begin
        insert into content_deleted (content_id, language_id, md_title, md_description, content, created_at, updated_at, deleted_at)
        values (old.content_id, old.language_id, old.md_title, old.md_description, old.content, old.created_at, old.updated_at, current_timestamp)
        on conflict (content_id, language_id)
        do update set
            md_title = excluded.md_title,
            md_description = excluded.md_description,
            content = excluded.content,
            created_at = excluded.created_at,
            updated_at = excluded.updated_at,
            deleted_at = current_timestamp;
        return old;
    end;
    $$ language plpgsql;
    """),
    text("""create trigger trigger_move_to_content_deleted
    before delete on content
    for each row execute function move_to_content_deleted();
    """),
    # Deal history
    text(
        """
        create or replace function save_deal_state()
        returns trigger as $$
        begin
            insert into deal_history
            (
                deal_id, sale_stage_id,
                probability, lost_reason_id,
                manager_id, lost_reason_additional_text,
                changed_at
            )
            values
            (
                old.deal_id, old.sale_stage_id,
                old.probability, old.lost_reason_id,
                old.manager_id, old.lost_reason_additional_text,
                current_timestamp
            );
            if tg_op = 'UPDATE' then
                return new;
            elsif tg_op = 'DELETE' then
                return old;
            end if;
        end;
        $$ language plpgsql;
        """
    ),
    text(
        """
        create trigger trigger_save_deal_state_version
        before update or delete on deal
        for each row execute function save_deal_state();
        """
    ),
]
