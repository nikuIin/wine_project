from uuid import UUID

from pydantic import BaseModel, Field

from core.config import auth_settings

BASE_TOKEN_TYPE = auth_settings.token_type


class TokensResponse(BaseModel):
    access_token: str = Field(
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTRkOWNjNzYtMDBkZS00ZWEyLTkxZWQtM2I3MGJiM2M2Y2QzIiwidG9rZW5faWQiOiIwMGM3OWQwMy0xM2MzLTQ0MzctYjQwMy1lYzBiZTUyMjE0N2EiLCJsb2dpbiI6Im15X2Nvb2xfbG9naW4iLCJyb2xlX2lkIjoxLCJleHBpcmVfZGF0ZSI6MTc0OTg3Nzk4NC4yMDAyMjl9.x_QQ7PywmGI9VPxpeaRtDEAzvlfTw26eLv2akYlpPlU",
        ]
    )
    refresh_token: str = Field(
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTRkOWNjNzYtMDBkZS00ZWEyLTkxZWQtM2I3MGJiM2M2Y2QzIiwidG9rZW5faWQiOiIwMGM3OWQwMy0xM2MzLTQ0MzctYjQwMy1lYzBiZTUyMjE0N2EiLCJsb2dpbiI6Im15X2Nvb2xfbG9naW4iLCJyb2xlX2lkIjoxLCJleHBpcmVfZGF0ZSI6MTc0OTg3Nzk4NC4yMDAyMjl9.xRg76wjfq4U8Z_yNRhyU-49HFK2BQ3UZZEI-40HM8VE",
        ]
    )
