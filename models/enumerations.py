from enum import Enum

class Gender(Enum):
    male = 1
    female = 2


class Scholing(Enum):
    primary = 1
    secondary = 2
    pre_university = 3
    university = 4
    middle_technical = 5


class SortBy(Enum):
    first_name = "first_name"
    second_name = "second_name"
    last_name = "last_name"
    birth_date = "birth_date"
    gender = "gender"
    height = "height"
    weight = "weight"
    scholing = "scholing"
    employee = "employee"
    married = "married"


class Order(Enum):
    asc = "asc"
    desc = "desc"