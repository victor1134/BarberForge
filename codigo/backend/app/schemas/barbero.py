from pydantic import BaseModel, ConfigDict


class BarberoIn(BaseModel):
    email: str
    full_name: str
    id_number: str
    password: str
    specialties: str = ""
    service_ids: list[int] = []


class BarberoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    is_active: bool
    specialties: str
    service_ids: list[int]
