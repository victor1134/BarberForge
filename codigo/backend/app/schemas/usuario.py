from pydantic import BaseModel, ConfigDict


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    style_pref: str = ""


class RegistroIn(BaseModel):
    email: str
    full_name: str
    id_type: str = "CC"
    id_number: str
    password: str
    accept_policy: bool = False


class LoginIn(BaseModel):
    email: str
    password: str


class SesionOut(BaseModel):
    token: str
    user: UsuarioOut


class CuentaIn(BaseModel):
    full_name: str | None = None
    email: str | None = None
    style_pref: str | None = None
    current_password: str | None = None
    new_password: str | None = None


class CuentaOut(BaseModel):
    user: UsuarioOut


class SetupOut(BaseModel):
    hay_admin: bool
