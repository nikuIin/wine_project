from sqlalchemy import text

GET_USER_CREDS = text(
    """
    select
      user_id,
      login,
      password,
      role_id
    from "user"
    where login = :login;
    """
)


CREATE_USER = text(
    """
    insert into "user"(user_id, login, password, role_id, created_at)
    values(:user_id, :login, :password, :role_id, current_timestamp)
    """
)

UPDATE_USER = text(
    """
    update "user" set
      password = :password,
      role_id = :role_id,
      updated_at = current_timestamp
    where login = :login;
    """
)
