# Declares each of the most likely http exceptions

from fastapi.exceptions import HTTPException
from fastapi import status


def exception_already_exists(data, detail: dict, status_code: status=status.HTTP_409_CONFLICT):
    if data:
        raise HTTPException(status_code, detail)
    return

def exception_not_exists(data, detail: dict, status_code: status=status.HTTP_404_NOT_FOUND):
    if not data:
        raise HTTPException(status_code, detail)
    return