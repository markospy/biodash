from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"


class Scholing(str, Enum):
    primary = "primary"
    secondary = "secondary"
    pre_university = "pre university"
    university = "university"
    middle_technical = "middle_technical"
    other = "other"


class SortBy(str, Enum):
    first_name = "first_name"
    last_name = "last_name"
    birth_date = "birth_date"
    gender = "gender"
    height = "height"
    weight = "weight"
    employee = "employee"
    married = "married"


class FilterBy(str, Enum):
    first_name = "first_name"
    last_name = "last_name"
    birth_date = "birth_date"
    gender = "gender"
    height = "height"
    weight = "weight"
    scholing = "scholing"
    employee = "employee"
    married = "married"


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class Operation(str, Enum):
    minimum = "max"
    maximum = "min"
    mean = "mean"
