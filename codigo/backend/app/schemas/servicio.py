from pydantic import BaseModel, ConfigDict


class ServicioIn(BaseModel):
    name: str
    description: str = ""
    price_cop: int
    duration_minutes: int
    service_type: str = "corte"


class ServicioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price_cop: int
    duration_minutes: int
    service_type: str
    is_active: bool
