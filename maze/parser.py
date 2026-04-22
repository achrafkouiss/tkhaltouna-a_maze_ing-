import os
import sys
from typing import Annotated, Tuple
from pydantic import BaseModel, BeforeValidator, field_validator, Field, model_validator, ValidationError

required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]

def _split_string(cordinates: str):
        if isinstance(cordinates, str):
            return cordinates.split(",")
        return cordinates

class Datavalidator(BaseModel):
    width: Annotated[int, Field(gt=0, lt=200)]
    height: Annotated[int, Field(gt=0, lt=200)]
    entry: Annotated[Tuple[int, int], BeforeValidator(_split_string)]
    exit: Annotated[Tuple[int, int], BeforeValidator(_split_string)]
    output_file: str
    perfect: bool 

    @model_validator(mode='after')
    def validate_input(self) -> str:
        if self.entry == self.exit:
            raise ValueError("entry and exit should be different")
        x, y = self.entry
        xn, yn = self.exit
        if not (0 <= x < self.width and 0 <= x < self.height) or \
        not (0 <= xn < self.width and 0 <= yn < self.height):
            raise ValueError(
                f"Entry {self.entry} out of bounds "
                f"(width={self.width}, height={self.height})"
            )
        return self

    @field_validator('output_file')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.endswith('.txt'):
            raise ValueError('filename must end with .txt')
        if v == 'config.txt':
            raise ValueError('filename cannot be config.txt')
        return v
    
@staticmethod
def config_parsing(file_name: str):
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"{file_name} not found")
    #make sure to handlle the case if i don't have the permision
    with open(file_name) as file:
        config = []
        for line in file:
            if line.startswith("#") or line == "\n":
                continue
            striped_line = "".join(line.split())
            a = striped_line.split("=", 1)
            config.append(striped_line.split("=", 1))
        values = dict(config)
        keys = [key for key in values.keys()]
        valid = set(required_keys).issubset(keys) 
        if not all(key.isupper() for key in keys):
            raise ValueError("All key should be uppercase")
        elif not set(required_keys).issubset(keys):
            raise ValueError("(WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT) all these keys need to exist")
        lower_dict = {k.lower(): v for k, v in values.items()}
        try:
            configuration = Datavalidator(**lower_dict)
        except ValidationError as e:
            print("[ERROR] Configuration validation failed:")
            for err in e.errors():
                loc = "".join(map(str, err["loc"]))
                msg = err["msg"]
                print(f"  - {loc}: {msg}")
                sys.exit(1)
        return configuration

