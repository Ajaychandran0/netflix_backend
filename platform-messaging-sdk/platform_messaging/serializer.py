import json
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


def serialize_event(data: dict[str, Any]) -> dict[str, str]:
    payload: dict[str, str] = {}

    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, (dict, list)):
            payload[key] = json.dumps(value)

        elif isinstance(value, datetime):
            payload[key] = value.isoformat()

        elif isinstance(value, uuid.UUID):
            payload[key] = str(value)

        elif isinstance(value, Decimal):
            payload[key] = str(value)

        elif isinstance(value, Enum):
            payload[key] = value.value

        else:
            payload[key] = str(value)

    return payload