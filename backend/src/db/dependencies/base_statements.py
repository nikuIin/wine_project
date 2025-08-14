from sqlalchemy import insert, text

from db.models import Country, LostReason, Role, SaleStage
from db.statement import Statement

SCHEMAS_LIST = (
    "ref",
    "crm",
    "auth",
    "catalog",
    "grape",
)

INSERT_LOST_REASON = text(
    """
        insert into lost_reason (lost_reason_id, name)
        overriding system value values (:lost_reason_id, :name)
        on conflict (lost_reason_id) do nothing;
    """
)

INSERT_SALE_STAGE = text(
    """
    insert into sale_stage (
        sale_stage_id, name,
        description, next_sale_stage_id
    )
    overriding system value values (
        :sale_stage_id, :name,
        :description, :next_sale_stage_id)
    on conflict (sale_stage_id) do nothing;
    """
)

INSERT_ROLE_STMT = text(
    """
    insert into role (role_id, name) values (:role_id, :name)
    on conflict (role_id) do nothing;
    """
)

# Tuple of insert statements for initial data loading
# TODO: add statuses, roles and reformat insert country data.
BASE_STATEMENTS: tuple[Statement, ...] = (
    Statement(
        description="Add role 'admin'",
        statement=INSERT_ROLE_STMT,
        data={"role_id": 2, "name": "admin"},
        check_query=lambda session: session.query(Role).filter_by(
            role_id=2,
        ),
    ),
    Statement(
        description="Add role 'user'",
        statement=INSERT_ROLE_STMT,
        data={"role_id": 1, "name": "lead"},
        check_query=lambda session: session.query(Role).filter_by(
            role_id=1,
        ),
    ),
    Statement(
        description="Add lost reason 'High price'",
        statement=INSERT_LOST_REASON,
        data={"lost_reason_id": 1, "name": "Высокая цена"},
        check_query=lambda session: session.query(LostReason).filter_by(
            lost_reason_id=1
        ),
    ),
    Statement(
        description="Add lost reason 'Lack of wine-specific features'",
        statement=INSERT_LOST_REASON,
        data={
            "lost_reason_id": 2,
            "name": "Отсутствие специфических функций для виноделия",
        },
        check_query=lambda session: session.query(LostReason).filter_by(
            lost_reason_id=2
        ),
    ),
    Statement(
        description="Add lost reason 'Complexity or difficulty of use'",
        statement=INSERT_LOST_REASON,
        data={
            "lost_reason_id": 3,
            "name": "Сложность или трудность использования",
        },
        check_query=lambda session: session.query(LostReason).filter_by(
            lost_reason_id=3
        ),
    ),
    Statement(
        description="Add lost reason 'No perceived need or satisfaction with current system'",
        statement=INSERT_LOST_REASON,
        data={
            "lost_reason_id": 4,
            "name": "Отсутствие видимой потребности или удовлетворенность текущей системой",
        },
        check_query=lambda session: session.query(LostReason).filter_by(
            lost_reason_id=4
        ),
    ),
    Statement(
        description="Add sale stage 'Исполнение'",
        statement=INSERT_SALE_STAGE,
        data={
            "sale_stage_id": 6,
            "name": "Исполнение",
            "description": "Оплаченный заказ, ожидает или на этапе исполнения",
            "next_sale_stage_id": None,
        },
        check_query=lambda session: session.query(SaleStage).filter_by(
            sale_stage_id=6
        ),
    ),
    Statement(
        description="Add sale stage 'Оплата'",
        statement=INSERT_SALE_STAGE,
        data={
            "sale_stage_id": 5,
            "name": "Оплата",
            "description": "Заказ ожидает оплаты",
            "next_sale_stage_id": 6,
        },
        check_query=lambda session: session.query(SaleStage).filter_by(
            sale_stage_id=5
        ),
    ),
    Statement(
        description="Add sale stage 'Переговоры'",
        statement=INSERT_SALE_STAGE,
        data={
            "sale_stage_id": 4,
            "name": "Переговоры",
            "description": "Согласование условий и закрытие сделки",
            "next_sale_stage_id": 5,
        },
        check_query=lambda session: session.query(SaleStage).filter_by(
            sale_stage_id=4
        ),
    ),
    Statement(
        description="Add sale stage 'Предложение'",
        statement=INSERT_SALE_STAGE,
        data={
            "sale_stage_id": 3,
            "name": "Предложение",
            "description": "Подготовка и презентация коммерческого предложения",
            "next_sale_stage_id": 4,
        },
        check_query=lambda session: session.query(SaleStage).filter_by(
            sale_stage_id=3
        ),
    ),
    Statement(
        description="Add sale stage 'Квалификация'",
        statement=INSERT_SALE_STAGE,
        data={
            "sale_stage_id": 2,
            "name": "Квалификация",
            "description": "Оценка потребностей и возможностей клиента",
            "next_sale_stage_id": 3,
        },
        check_query=lambda session: session.query(SaleStage).filter_by(
            sale_stage_id=2
        ),
    ),
    Statement(
        description="Add sale stage 'Первичный контакт'",
        statement=INSERT_SALE_STAGE,
        data={
            "sale_stage_id": 1,
            "name": "Первичный контакт",
            "description": "Первый контакт с потенциальным клиентом",
            "next_sale_stage_id": 2,
        },
        check_query=lambda session: session.query(SaleStage).filter_by(
            sale_stage_id=1
        ),
    ),
)
