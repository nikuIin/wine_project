CREATE OR REPLACE FUNCTION update_tsvector()
RETURNS TRIGGER AS $$
DECLARE
    language VARCHAR = (
        SELECT cfgname
        FROM language
        WHERE language_id = NEW.language_id
    );
    to_tsv_title varchar = regexp_replace(NEW.title, '[^[:alnum:] ]', '', 'g'); -- оставляем цифры
    to_tsv_content text = regexp_replace(regexp_replace(NEW.content, '<br />', '', 'g'), '[^[:alnum:] ]', '', 'g'); -- оставляем цифры
BEGIN
    IF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = language) THEN
        NEW.tsv_content :=
            setweight(to_tsvector(language::regconfig, to_tsv_title), 'A') ||
            setweight(to_tsvector(language::regconfig, to_tsv_content), 'B');
    ELSE
        NEW.tsv_content :=
            setweight(to_tsvector('simple'::regconfig, to_tsv_title), 'A') ||
            setweight(to_tsvector('simple'::regconfig, to_tsv_content), 'B');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


create or replace TRIGGER tsvector_update
BEFORE INSERT OR UPDATE
ON article_translate
FOR EACH ROW
EXECUTE FUNCTION update_tsvector();

CREATE INDEX article_translate_idx ON article_translate USING GIN(tsv_content);
