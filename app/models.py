from enum import Enum
from typing import List, Dict

class ModelType(Enum):
    RGB = "rgb"
    MIX = "mix"

class Model:
    def __init__(self, name: str, types: List[ModelType]):
        if not name:
            raise ValueError("The model name cannot be empty")
        self.name = name

        self.types = []
        for type in types:
            try:
                enum_type = ModelType[type]
                self.types.append(enum_type)
            except KeyError:
                raise ValueError(f"The type {type} is not a valid model type. Valid types are: {ModelType.__members__}")
        if not self.types:
            raise ValueError(f"You must specify at least one valid model type. Valid types are: {ModelType.__members__}")