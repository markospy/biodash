import os
import enum
from dotenv import load_dotenv
from datetime import datetime as dt

load_dotenv()
usuario = os.getenv("USER")
contraseña = os.getenv("PASSWORD")
localhost = os.getenv("LOCALHOST")
puerto = os.getenv("PORT")
base_de_datos = os.getenv("BD")

from sqlalchemy import (
    Enum,
    create_engine,
    ForeignKey,
    Table,
    Column,
    UniqueConstraint,
)
from sqlalchemy.types import String, DateTime, JSON
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Gender(enum.Enum):
    male = 1
    female = 2


class Scholing(enum.Enum):
    primary = 1
    secondary = 2
    pre_university = 3
    university = 4
    middle_technical = 5


class Email(Base):
    __tablename__ = "email"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email_address: Mapped[str] = mapped_column(String(30))
    email_verify: Mapped[bool] = mapped_column(default=False)
    code: Mapped[int]
    doctor_id: Mapped[str] = mapped_column(
        String(30), ForeignKey("doctors.id", ondelete="CASCADE")
    )
    doctor = relationship("Doctor", back_populates="email")


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address = mapped_column(JSON)
    patient = relationship("Patient", back_populates="address")


doctor_patient = Table(
    "doctor_patient",
    Base.metadata,
    Column(
        "doctor_id", String(30), ForeignKey("doctors.id", ondelete="CASCADE")
    ),
    Column(
        "patient_id", String(30), ForeignKey("patients.id", ondelete="CASCADE")
    ),
    UniqueConstraint("doctor_id", "patient_id", name="uix_1"),
)


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    second_name: Mapped[str | None] = mapped_column(String(30))
    last_name: Mapped[str | None] = mapped_column(String(30))
    specialty: Mapped[str | None] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(255))
    portrait: Mapped[str | None] = mapped_column(String(100))
    patients: Mapped[list["Patient"]] = relationship(
        secondary=doctor_patient,
        cascade="all, delete",
        back_populates="doctors",
    )
    email = relationship(
        "Email", back_populates="doctor", cascade="all, delete"
    )

    measure_cvs: Mapped[list["CardiovascularParameter"]] = relationship(
        back_populates="doctor", cascade="all, delete"
    )
    measure_blood_sugar: Mapped[list["BloodSugarLevel"]] = relationship(
        back_populates="doctor", cascade="all, delete"
    )


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    second_name: Mapped[str | None] = mapped_column(String(30))
    last_name: Mapped[str | None] = mapped_column(String(30))
    birth_date: Mapped[dt | None] = mapped_column(DateTime)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender))
    height: Mapped[int | None]
    weight: Mapped[float | None]
    scholing: Mapped[Scholing | None]
    employee: Mapped[bool | None]
    married: Mapped[bool | None]
    doctors: Mapped[list["Doctor"]] = relationship(
        secondary=doctor_patient,
        cascade="all, delete",
        back_populates="patients",
    )
    address_id: Mapped[int | None] = mapped_column(ForeignKey("address.id"))
    address = relationship(
        "Address", back_populates="patient", cascade="all, delete"
    )
    measure_cvs: Mapped[list["CardiovascularParameter"]] = relationship(
        back_populates="patient", cascade="all, delete"
    )
    measure_blood_sugar: Mapped[list["BloodSugarLevel"]] = relationship(
        back_populates="patient", cascade="all, delete"
    )


class CardiovascularParameter(Base):
    __tablename__ = "cardiovascular_parameters"

    date = mapped_column(DateTime(timezone=True), primary_key=True)
    systolic: Mapped[int] = mapped_column(default=120)
    diastolic: Mapped[int] = mapped_column(default=80)
    heart_rate: Mapped[int | None] = mapped_column(default=None)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), primary_key=True
    )
    doctor_id: Mapped[str] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE")
    )
    patient = relationship("Patient", back_populates="measure_cvs")
    doctor = relationship("Doctor", back_populates="measure_cvs")


class BloodSugarLevel(Base):
    __tablename__ = "blood_sugar_levels"

    date = mapped_column(DateTime(timezone=True), primary_key=True)
    value: Mapped[float]
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), primary_key=True
    )
    doctor_id: Mapped[str] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE")
    )
    patient = relationship("Patient", back_populates="measure_blood_sugar")
    doctor = relationship("Doctor", back_populates="measure_blood_sugar")


# Motor sqlite
# engine = create_engine("sqlite:///db/base.db", echo=True)

# Motor mysql local
# engine = create_engine("mysql+pymysql://marcos:mypassword@localhost/bio_parameters_control?charset=utf8mb4")

# Motor mysql en la nube
engine = create_engine(
    f"mysql+mysqldb://{usuario}:{contraseña}@{localhost}:{puerto}/{base_de_datos}"
)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(engine)
