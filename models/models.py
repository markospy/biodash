import enum
from datetime import datetime as dt

from sqlalchemy import Enum, create_engine, ForeignKey, func, Table, Column
from sqlalchemy.types import String, BLOB, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship


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

    email_id: Mapped[int] = mapped_column(String(30), primary_key=True, autoincrement=True)
    email_adreess: Mapped[str] = mapped_column(String(30))
    email_verify: Mapped[bool] = mapped_column(default=False)
    doctor_id: Mapped[str] = mapped_column(String(30), ForeignKey("doctors.doctor_id"))
    doctor = relationship("Doctor", back_populates="email")


class Adress(Base):
    __tablename__ = "adress"

    adress_id: Mapped[int] = mapped_column(String(30), primary_key=True, autoincrement=True)
    adress = mapped_column(JSON)
    patient = relationship("Patient", back_populates="adress")


doctor_patient = Table(
    "doctor_patient",
    Base.metadata,
    Column("doctor_id", String(30), ForeignKey("doctors.doctor_id")),
    Column("patient_id", String(30), ForeignKey("patients.patient_id")),
)


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    second_name: Mapped[str | None] = mapped_column(String(30))
    last_name: Mapped[str | None] = mapped_column(String(30))
    specialty: Mapped[str | None] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(255))
    portrait = mapped_column(BLOB, nullable=True)
    patients: Mapped[list["Patient"]] = relationship(secondary=doctor_patient, cascade="all, delete")
    email = relationship("Email", back_populates="doctor", cascade="all, delete")
    measure_cvs: Mapped[list["CardiovascularParameter"]] = relationship(
        back_populates="doctor", cascade="all, delete"
    )
    measure_blood_sugar: Mapped[list["CardiovascularParameter"]] = relationship(
        back_populates="doctor", cascade="all, delete"
    )


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(String(30), primary_key=True)
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
    adress_id: Mapped[int] = mapped_column(ForeignKey("adress.adress_id"))
    adress: Mapped[Adress] = relationship(back_populates="adress", cascade="all, delete")
    doctors: Mapped[list["Doctor"]] = relationship(secondary=doctor_patient, cascade="all, delete")
    measure_cvs: Mapped[list["CardiovascularParameter"]] = relationship(
        back_populates="patient", cascade="all, delete"
    )
    measure_blood_sugar: Mapped[list["CardiovascularParameter"]] = relationship(
        back_populates="patient", cascade="all, delete"
    )


class CardiovascularParameter(Base):
    __tablename__ = "cardiovascular_parameters"

    date = mapped_column(DateTime(timezone=True), primary_key=True)
    systolic: Mapped[int] = mapped_column(default=120)
    diastolic: Mapped[int] = mapped_column(default=80)
    heart_rate: Mapped[int | None] = mapped_column(default=None)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.patient_id", ondelete="CASCADE"), primary_key=True
    )
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.doctor_id", ondelete="CASCADE"))
    patient = relationship("Patient", back_populates="measure_cvs")
    doctor = relationship("Doctor", back_populates="measure_cvs")


class BloodSugarLevel(Base):
    __tablename__ = "blood_sugar_levels"

    date = mapped_column(DateTime(timezone=True), primary_key=True)
    value = Mapped[float]
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.patient_id", ondelete="CASCADE"), primary_key=True
    )
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.doctor_id", ondelete="CASCADE"))
    patient = relationship("Patient", back_populates="measure_blood_sugar")
    doctor = relationship("Doctor", back_populates="measure_blood_sugar")


# Motor sqlite
engine = create_engine("sqlite:///db/base.db", echo=True)

# Motor mysql
# engine = create_engine("mysql+pymysql://marcos:mypassword@localhost/bio_parameters_control?charset=utf8mb4")

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(engine)
