import enum

from sqlalchemy import Enum, create_engine, ForeignKey, func, DateTime, String
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


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), primary_key=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    patient_relarionship: Mapped[list["Patient"]] = relationship(
        back_populates="username_relarionship", cascade="all, delete"
    )


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    second_name: Mapped[str | None] = mapped_column(String(30))
    last_name: Mapped[str | None] = mapped_column(String(30))
    age: Mapped[int | None]
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender))
    height: Mapped[int | None]
    weight: Mapped[float | None]
    username: Mapped["User"] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    username_relarionship = relationship("User", back_populates="patient_relarionship")
    measure: Mapped[list["BloodPressure"]] = relationship(
        back_populates="patient", cascade="all, delete"
    )


class BloodPressure(Base):
    __tablename__ = "blood_pressure"

    systolic: Mapped[int] = mapped_column(default=120)
    diastolic: Mapped[int] = mapped_column(default=80)
    heart_rate: Mapped[int | None] = mapped_column(default=None)
    date = mapped_column(DateTime(timezone=True), primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), primary_key=True
    )
    patient = relationship("Patient", back_populates="measure")


# Motor sqlite
# engine = create_engine("sqlite:///db/base.db", echo=True)

# Motor mysql
engine = create_engine(
    "mysql+pymysql://myuser:mypassword@localhost/mydb?charset=utf8mb4"
)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(engine)
