from typing import Dict

from pydantic import BaseModel


class RequestMetadataResponse(BaseModel):
    total_requests: int
    path_total: Dict[str, int]
    status_total: Dict[str, int]
    failure_total: Dict[str, int]

