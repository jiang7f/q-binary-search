from dataclasses import dataclass
from ...provider import Provider

@dataclass(kw_only=True)
class CircuitOption():
    provider: Provider
    shots: int = 1024