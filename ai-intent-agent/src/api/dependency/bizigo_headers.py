from fastapi import Header
from src.api.schemas.header_schema import BizigoHeader


async def bizigo_headers(
        application_id: str = Header(..., alias="Applicationid"),
        user_id: str = Header(..., alias="Userid"),
        language_code: str = Header(..., alias="LanguageCode"),
        country_code: str = Header(default="TR", alias="CountryCode"),
        currency_code: str = Header(default="TRY", alias="CurrencyCode"),
        bearer: str = Header(..., alias="Bearer"),
) -> dict:
    bzg_hdr = BizigoHeader(
        ApplicationId=application_id,
        UserId=user_id,
        LanguageCode=language_code,
        Bearer=bearer,
        CountryCode=country_code,
        CurrencyCode=currency_code,
    )
    return bzg_hdr.as_dict()