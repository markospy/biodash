import enum

from sqlalchemy import Enum, ForeignKey, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Gender(enum.Enum):
    male = 1
    female = 2


class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    second_name: Mapped[str | None]
    last_name: Mapped[str | None]
    age: Mapped[int | None]
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender))
    height: Mapped[int | None]  # altura en centímetros
    weight: Mapped[float | None]  # peso en kilogramos
    measure: Mapped[list["BloodPressure"]] = relationship(
        back_populates="user", cascade="all, delete"
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="measure")
