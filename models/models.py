import enum

from sqlalchemy import Enum, ForeignKey, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Gender(enum.Enum):
    male = 1
    female = 2


class User(Base):
    __tablename__ = "user"

    usename: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str]
    patient_relarionship: Mapped[list["Patient"]] = relationship(
        back_populates="username_relarionship", cascade="all, delete"
    )


class Patient(Base):
    __tablename__ = "patients"

    id_patient: Mapped[str] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    second_name: Mapped[str | None]
    last_name: Mapped[str | None]
    age: Mapped[int | None]
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender))
    height: Mapped[int | None]  # altura en centímetros
    weight: Mapped[float | None]  # peso en kilogramos
    username: Mapped["User"] = mapped_column(ForeignKey("user.username"))
    username_relarionship: Mapped["User"] = relationship(
        back_populates="patient_relarionship"
    )
    measure: Mapped[list["BloodPressure"]] = relationship(
        back_populates="patient", cascade="all, delete"
    )


class BloodPressure(Base):
    __tablename__ = "blood_pressure"

    systolic: Mapped[int] = mapped_column(default=120)
    diastolic: Mapped[int] = mapped_column(default=80)
    heart_rate: Mapped[int | None] = mapped_column(default=None)
    date = mapped_column(DateTime(timezone=True), server_default=func.now())
    hour = mapped_column(
        DateTime(timezone=True), server_default=func.now(), primary_key=True
    )
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), primary_key=True)

    patient: Mapped["Patient"] = relationship(back_populates="measure")
