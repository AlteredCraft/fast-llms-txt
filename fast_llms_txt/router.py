"""FastAPI router for serving llms.txt."""

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from .generator import generate_llms_txt, get_operation_spec


def create_llms_txt_router(app: FastAPI, path: str = "/llms.txt") -> APIRouter:
    """Create a router that serves the llms.txt endpoint.

    Args:
        app: The FastAPI application instance
        path: The path to mount the endpoint at (default: /llms.txt)

    Returns:
        An APIRouter that can be included in the app

    Example:
        >>> from fastapi import FastAPI
        >>> from fast_llms_txt import create_llms_txt_router
        >>>
        >>> app = FastAPI(title="My API")
        >>> app.include_router(create_llms_txt_router(app), prefix="/docs")
    """
    router = APIRouter()

    @router.get(
        path,
        response_class=PlainTextResponse,
        include_in_schema=False,
        summary="Get LLM-friendly API documentation",
    )
    def get_llms_txt() -> str:
        """Return the API documentation in llms.txt markdown format."""
        openapi_schema = app.openapi()
        return generate_llms_txt(openapi_schema, path)

    @router.get(
        f"{path}/paths/{{method}}/{{api_path:path}}",
        response_class=JSONResponse,
        include_in_schema=False,
        summary="Get OpenAPI spec for a single operation",
    )
    def get_operation_openapi(method: str, api_path: str) -> JSONResponse:
        """Return the OpenAPI spec for a specific method+path with resolved refs."""
        openapi_schema = app.openapi()
        # FastAPI strips the leading slash from path parameters
        full_path = f"/{api_path}"
        spec = get_operation_spec(openapi_schema, method, full_path)
        if spec is None:
            raise HTTPException(
                status_code=404,
                detail=f"Operation {method.upper()} {full_path} not found",
            )
        return JSONResponse(content=spec)

    return router
