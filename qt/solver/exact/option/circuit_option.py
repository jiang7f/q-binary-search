from dataclasses import dataclass
from qt.circuit import CircuitOption

@dataclass(kw_only=True)
class QbsCircuitOption(CircuitOption):
    mcx_mode: str # 'constant' for 2 additional ancillas with linear depth, 'linear' for n - 1 additional ancillas with logarithmic depth
    repeat: int = None
