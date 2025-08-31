from pydantic import BaseModel, Field

class BizigoHeader(BaseModel):
    ApplicationId: str
    UserId: str
    LanguageCode: str
    CountryCode: str = Field(default="TR")
    CurrencyCode: str = Field(default="TRY")
    Bearer: str

    def as_dict(self):
        return {
            "ApplicationId": self.ApplicationId,
            "UserId": self.UserId,
            "LanguageCode": self.LanguageCode,
            "CountryCode": "TR",
            "CurrencyCode": "TRY",
            "Bearer": self.Bearer,
        }