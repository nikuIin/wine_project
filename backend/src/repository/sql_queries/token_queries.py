from sqlalchemy.sql import text

IS_TOKEN_IN_BLACK_LIST = text(
    """
    select
      true as is_in_black_list
    from black_refresh_token_list
    where refresh_token_id = :refresh_token_id
    """
)

CREATE_OR_UPDATE_REFRESH_TOKEN = text(
    """
    insert into refresh_token(
      refresh_token_id,
      user_id,
      expire_at
    ) values (:refresh_token_id, :user_id, :expire_at)
    on conflict(refresh_token_id) do update
    set expire_at = :expire_at
    """
)
