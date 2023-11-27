from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BloodPressure(Base):
    __tablename__ = "blood_pressure"

    systolic: Mapped[int] = mapped_column(default=120, nullable=False)
    diastolic: Mapped[int] = mapped_column(default=80, nullable=False)
    heart_rate: Mapped[int | None] = mapped_column(default=None)
    date = mapped_column(DateTime(timezone=True), server_default=func.now())
    hour = mapped_column(primary_key=True, DateTime(timezone=True), server_default=func.now())
    user_id: mapped_column[int] = mapped_column(primary_key=True, ForeignKey("users.id"))

    
