from pydantic import BaseModel, EmailStr, validator, Field

from datetime import datetime

from models.enumerations import Gender, Scholing


class EmailSchema(BaseModel):
    email_address: EmailStr
    email_verify: bool = False
    code: int
    doctor_id: str


class AddressSchema(BaseModel):
    address_id: int
    address: dict = Field(example={'Provincia':'Ciefuegos', 'Barrio':'Pastorita'}, description='Recibe un objeto')


class Doctor(BaseModel):
    id: str = Field(example='3210', description="El formato de este id es distinto en cada país, puede ser un número o una cadena de letras y dígitos")
    first_name: str = Field(example='Marcos Antonio')
    last_name: str = Field(example='Avila Morales')
    specialty: str = Field(example='Médico General')
    email_address: str | None = Field(example='markos@email.com', pattern='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', default=None)


class DoctorOut(Doctor):
    email_verify: bool
    photo: str | None = None


class DoctorIn(Doctor):
    password: str = Field(min_length=6, example='jH3.*3tH2nAs_p')


class DoctorUp(DoctorIn):
    id: str | None = None
    first_name: str | None = None
    password: str | None = None

    @validator("*", pre=True, allow_reuse=True)
    def check_null_values(cls, value):
        if value == "null":
            return None
        return value


class DoctorPhoto(Doctor):
    portrait: str | None = None


class PatientSchema(BaseModel):
    id: str = Field(example='39231', description='Debería usarse el CI del paciente o su código identificativo en el sistema de salud de su país')
    first_name: str = Field(example="Javier")
    last_name: str = Field(example="Hernandez Lao")
    birth_date: datetime | None = Field(default=None, example="04-29-1979")
    gender: Gender | None = Field(default=None, examples=["female", "male"], description='Solo puede recibir alguno de los valores de ejemplo')
    height: int | None = Field(default=None, example=180)
    weight: float | None = Field(default=None, example=80)
    scholing: Scholing | None = Field(default=None, examples=["primary", "secunadry", "pre_university", "university", "middle_technical"], description='Solo puede recibir alguno de los valores de ejemplo')
    employee: bool | None = Field(default=None, example="Mechanic")
    married: bool | None = Field(default=None, example=True)
    address: dict | None = Field(default=None, example={'Provincia':'Ciefuegos', 'Barrio':'Pastorita'}, description='Recibe un objeto')


class PatientUp(PatientSchema):
    id: str | None = None
    first_name: str | None = None

    @validator("*", pre=True, allow_reuse=True)
    def check_null_values(cls, value):
        if value == "null":
            return None
        return value


class DoctorPatient(BaseModel):
    doctor_id: str = Field(example=3210)
    patient_id: str = Field(example=39231)


class CardiovascularParameterOut(BaseModel):
    systolic: int | None = Field(default=None, example=120)
    diastolic: int | None = Field(default=None, example=80)
    heart_rate: int | None = Field(default=None, example=72)
    date: datetime | None = Field(default=None, example="04-29-2024")


class CardiovascularParameter(CardiovascularParameterOut):
    systolic: int = 120
    diastolic: int = 80
    patient_id: str = Field(example=39231)


class BloodSugarLevelOut(BaseModel):
    date: datetime | None = Field(default=None, example="04-29-2024")
    value: float | None = Field(default=None, example=5.2)


class BloodSugarLevelIn(BloodSugarLevelOut):
    patient_id: str = Field(example=39231)


class Analize(BaseModel):
    minimum: float
    maximum: float
    mean: float

class AnalizeCardiovascular(BaseModel):
    systolic: Analize
    diastolic: Analize
    heart_rate: Analize