from fastapi.responses import JSONResponse
from typing import Any

def api_response(
    data: Any,
    message: str = "Success",
    status_code: int = 200,
    code: str = "SUCCESS"
):
    return JSONResponse(
        status_code=status_code,
        content={
            "message": message,
            "data": data,
            "statusCode": status_code,
            "code": code
        }
    )
