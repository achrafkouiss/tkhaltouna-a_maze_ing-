from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from typing import Tuple
import pathlib
import sys


class MazeConfig(BaseModel):
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    color: str = "white"
    seed: int | None = None

    @field_validator("color")
    @classmethod
    def color_must_be_known(cls, v: str) -> str:
        allowed_colors = [
            "white", "red", "green",
            "yellow", "blue", "magenta", "cyan"
        ]
        if v not in allowed_colors:
            raise ValueError(
                f"Color must be one of {allowed_colors}"
            )
        return v

    @model_validator(mode="after")
    def validate_all(self) -> "MazeConfig":
        # Entry / Exit must be inside bounds
        ex, ey = self.entry
        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ValueError(
                f"Entry {self.entry} out of bounds "
                f"(width={self.width}, height={self.height})"
            )

        xx, xy = self.exit
        if not (0 <= xx < self.width and 0 <= xy < self.height):
            raise ValueError(
                f"Exit {self.exit} out of bounds "
                f"(width={self.width}, height={self.height})"
            )

        # Entry != Exit
        if self.entry == self.exit:
            raise ValueError(
                "Entry and Exit cannot be the same"
            )

        return self


def parse_config_file(path: str) -> MazeConfig:
    config_dict = {}
    path_obj = pathlib.Path(path)

    if not path_obj.exists():
        print(f"[ERROR] Config file not found: {path}")
        sys.exit(1)

    allowed_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "COLOR",
        "SEED",
    }

    with path_obj.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                print(f"[ERROR] Invalid line (no =): {line}")
                sys.exit(1)

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # 🔴 Enforce strict uppercase
            if key != key.upper():
                print(f"[ERROR] Key must be uppercase: '{key}'")
                sys.exit(1)

            # 🔴 Check if key is allowed
            if key not in allowed_keys:
                print(f"[ERROR] Unknown key: {key}")
                sys.exit(1)

            # Parse the values
            try:
                if key in ("WIDTH", "HEIGHT"):
                    config_dict[key.lower()] = int(value)
                elif key in ("ENTRY", "EXIT"):
                    x, y = map(int, value.split(","))
                    config_dict[key.lower()] = (x, y)
                elif key == "PERFECT":
                    if value.lower() not in ("true", "false"):
                        raise ValueError("PERFECT must be True or False")
                    config_dict["perfect"] = value.lower() == "true"
                elif key == "OUTPUT_FILE":
                    config_dict["output_file"] = value
                elif key == "COLOR":
                    config_dict["color"] = value
                elif key == "SEED":
                    config_dict["seed"] = int(value)
            except ValueError as e:
                print(f"[ERROR] Invalid value for {key}: {value} ({e})")
                sys.exit(1)

    # 🔴 Check for missing mandatory keys
    required_keys = {"width", "height", "entry", "exit", "output_file", "perfect"}
    missing = required_keys - config_dict.keys()
    if missing:
        print(f"[ERROR] Missing required keys: {', '.join(missing)}")
        sys.exit(1)

    # Validate with Pydantic
    try:
        config = MazeConfig(**config_dict)
    except ValidationError as e:
        print("[ERROR] Configuration validation failed:")
        for err in e.errors():
            loc = ".".join(map(str, err["loc"]))
            msg = err["msg"]
            print(f"  - {loc}: {msg}")
        sys.exit(1)

    return config


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py config.txt")
        sys.exit(1)

    config = parse_config_file(sys.argv[1])
    print(config.model_dump_json(indent=4))