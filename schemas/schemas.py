from typing import List
from pydantic import BaseModel, EmailStr, validator, Field

from datetime import datetime

from models.enumerations import Gender, Scholing


class Doctor(BaseModel):
    id: str = Field(examples=["3210"], description="El identificador del doctor")
    first_name: str = Field(examples=["Marcos Antonio"])
    last_name: str = Field(examples=["Avila Morales"])
    specialty: str = Field(examples=["Médico General"])
    email_address: str | None = Field(
        examples=["doctor_mail@yahoo.com"], pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", default=None
    )


class DoctorOut(Doctor):
    email_verify: bool = Field(examples=[True], description="Si el correo ha sido verificado")
    photo: str | None = Field(
        default=None, examples=["http://biodash.com/photos/3210.png"], description="URL con el avatar del doctor"
    )
    patients: int = Field(description="Numeros de pacientes registrados por el médico", ge=0)


class DoctorIn(Doctor):
    password: str = Field(min_length=6, examples=["jH3.*3tH2nAs_p"])


class DoctorScopes(DoctorIn):
    scopes: list[str]


class DoctorUp(DoctorIn):
    id: str | None = Field(examples=["3210"], description="El identificador del doctor", default=None)
    first_name: str | None = Field(examples=["Marcos Antonio"], default=None)
    last_name: str | None = Field(examples=["Avila Morales"], default=None)
    specialty: str | None = Field(examples=["Médico General"], default=None)
    password: str | None = Field(min_length=6, examples=["jH3.*3tH2nAs_p"], default=None)

    @validator("*", pre=True, allow_reuse=True)
    def check_null_values(cls, value):
        if value == "null":
            return None
        return value


class DoctorPhoto(Doctor):
    portrait: str | None = None


class EmailSchema(BaseModel):
    email_address: EmailStr | None = None
    email_verify: bool = False
    code: int | None = None
    doctor_id: str


class AddressSchema(BaseModel):
    address_id: int
    address: dict = Field(examples=[{"Provincia": "Ciefuegos", "Barrio": "Pastorita"}], description="Recibe un objeto")


class PatientSchema(BaseModel):
    id: str = Field(
        examples=["39231"],
        description="Debería usarse el CI del paciente o su código identificativo en el sistema de salud de su país",
    )
    first_name: str = Field(examples=["Javier"])
    last_name: str = Field(examples=["Hernandez Lao"])
    birth_date: datetime | None = Field(default=None, examples=["2000-01-01T12:00:00"])
    gender: Gender | None = Field(
        default=None, examples=["female", "male"], description="Solo puede recibir alguno de los valores de ejemplo"
    )
    height: int | None = Field(default=None, examples=[180])
    weight: float | None = Field(default=None, examples=[80])
    scholing: Scholing | None = Field(
        default=None,
        examples=["primary", "secunadry", "pre university", "university", "middle technical"],
        description="Solo puede recibir alguno de los valores de ejemplo",
    )
    employee: bool | None = Field(default=None, examples=[True])
    married: bool | None = Field(default=None, examples=[True])
    password: str | None = Field(default=None, frozen=True)
    address: dict | None = Field(
        default=None, examples=[{"Provincia": "Ciefuegos", "Barrio": "Pastorita"}], description="Recibe un objeto"
    )


class PatientScopes(PatientSchema):
    scopes: list[str]


class PatientSchemeList(BaseModel):
    len: int | None = 0
    patients: list[PatientSchema] | None = None


class PatientUp(PatientSchema):
    id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None

    @validator("*", pre=True, allow_reuse=True)
    def check_null_values(cls, value):
        if value == "null":
            return None
        return value


class DoctorPatient(BaseModel):
    doctor_id: str
    patient_id: str


class CardiovascularParameterUpdate(BaseModel):
    systolic: int | None = None
    diastolic: int | None = None
    heart_rate: int | None = None
    date: datetime | None = None


class CardiovascularParameter(CardiovascularParameterUpdate):
    patient_id: str


class CardiovascularParameterOut(CardiovascularParameterUpdate):
    doctor_id: str


class CardiovascularParameterOutList(BaseModel):
    patient_id: int
    measures: List[CardiovascularParameterOut]


class BloodSugarLevelUpdate(BaseModel):
    date: datetime | None = None
    value: float | None = None


class BloodSugarLevel(BloodSugarLevelUpdate):
    patient_id: str | None = None


class BloodSugarLevelOut(BloodSugarLevelUpdate):
    doctor: str | None = None


class BloodSugarLevelOutList(BaseModel):
    patient_id: int
    measures: List[BloodSugarLevelOut]


class Analize(BaseModel):
    minimum: float
    maximum: float
    mean: float


class AnalizeCardiovascular(BaseModel):
    systolic: Analize
    diastolic: Analize
    heart_rate: Analize


class WarningBloodSugar(BaseModel):
    patient_id: str = Field(description="Id del paciente")
    first_name: str
    last_name: str
    value: float = Field(description="Valor de la glucemia")
    date: datetime = Field(description="Fecha y hora de registro")


class WarningCardiovascularParameter(CardiovascularParameter):
    first_name: str
    last_name: str
