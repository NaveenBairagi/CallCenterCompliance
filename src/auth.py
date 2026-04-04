"""API key authentication middleware."""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

from src.config import settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate the API key from the request header.

    Args:
        api_key: The API key extracted from x-api-key header.

    Returns:
        The validated API key string.

    Raises:
        HTTPException: 401 if key is missing or invalid.
    """
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide x-api-key header.",
        )
    if api_key != settings.API_SECRET_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return api_key
