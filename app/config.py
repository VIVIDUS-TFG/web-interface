from pathlib import Path
from typing import Any

from fastapi.responses import HTMLResponse
from pydantic_settings import BaseSettings
from typing import Any

APP_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):

    APP_DIR: Path = APP_DIR

    STATIC_DIR: Path = APP_DIR / 'static'
    TEMPLATE_DIR: Path = APP_DIR / 'templates'

    MODELS_CONFIG: Path = APP_DIR / 'config' / 'models_config.yml'

    VIDEOS_DIR: Path = APP_DIR / 'videos_dir'
    FEATURES_DIR: Path = APP_DIR / 'features_dir'

    FASTAPI_PROPERTIES: dict[str, Any] = {
        "title": "VIVIDUS Configurator",
        "description": "Web interface for configuring and testing models",
        "version": "0.0.1",
        "default_response_class": HTMLResponse,  # Change default from JSONResponse
    }

    DISABLE_DOCS: bool = True

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        """Creates dictionary of values to pass to FastAPI app
        as **kwargs.

        Returns:
            dict: This can be unpacked as **kwargs to pass to FastAPI app.
        """
        fastapi_kwargs = self.FASTAPI_PROPERTIES
        if self.DISABLE_DOCS:
            fastapi_kwargs.update(
                {
                    "openapi_url": None,
                    "openapi_prefix": None,
                    "docs_url": None,
                    "redoc_url": None,
                }
            )
        return fastapi_kwargs
