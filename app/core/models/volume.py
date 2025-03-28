from dataclasses import dataclass

@dataclass
class Volume:
    name: str
    driver: str = "local"
    mountpoint: str = ""
    context: str = "default"
