from dataclasses import dataclass

@dataclass
class Network:
    name: str
    id: str
    driver: str
    scope: str
    context: str = "default"
