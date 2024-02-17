import yaml
import httpx
from typing import List
from pathlib import Path 

from starlette.status import HTTP_200_OK

from app.models import Model

def mount_models(file_path: Path) -> List[Model]:
    """Create classifying models instances with the specified settings."""

    with file_path.open('r') as file:
        data = yaml.safe_load(file)

    models = []
    for item in data['models']:
        name = item.get('name')
        types = item.get('types', [])

        model = Model(name, types)
        models.append(model)

    return models

async def check_service_health(url: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code != HTTP_200_OK:
                return False
            return True
        except httpx.RequestError as e:
            return False
