# Declares each of the most likely http exceptions

from fastapi.exceptions import HTTPException
from fastapi import status


def exception_if_already_exists(data, detail, status_code=status.HTTP_409_CONFLICT):
    if data:
        raise HTTPException(status_code, detail)
    return


def exception_if_not_exists(data, detail, status_code=status.HTTP_404_NOT_FOUND):
    if not data:
        raise HTTPException(status_code, detail)
    return


class OperationError(Exception):
    def __init__(self, msj_error) -> None:
        self.msj_error = msj_error
