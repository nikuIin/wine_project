from pydantic import BaseModel, Field


class DataDeletedResponse(BaseModel):
    """
    This class sets format for deleted response.
    It is always using as response after any delete operation
    (in DELETE requests types)
    """

    deleted_rows_quantity: int = Field(ge=0)
