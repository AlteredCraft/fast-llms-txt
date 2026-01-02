"""Generate llms.txt markdown from FastAPI OpenAPI schema for AI agents."""

from .generator import generate_llms_txt, get_operation_spec
from .router import create_llms_txt_router

__all__ = ["create_llms_txt_router", "generate_llms_txt", "get_operation_spec"]
__version__ = "0.3.0"
