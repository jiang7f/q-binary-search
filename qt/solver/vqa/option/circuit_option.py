from dataclasses import dataclass, field
from typing import List, Callable, Tuple, Dict, Union

from qt.model import ModelOption
from qt.provider import Provider
from qt.circuit import CircuitOption
# from qiskit.providers import Backend, BackendV2
# from qiskit.transpiler import PassManager


@dataclass(kw_only=True)
class LayerCircuitOption(CircuitOption):
    num_layers: int

@dataclass(kw_only=True)
class ChCircuitOption(LayerCircuitOption):
    mcx_mode: str # 'constant' for 2 additional ancillas with linear depth, 'linear' for n - 1 additional ancillas with logarithmic depth

@dataclass(kw_only=True)
class RaCircuitOption(CircuitOption):
    mcx_mode: str # 'constant' for 2 additional ancillas with linear depth, 'linear' for n - 1 additional ancillas with logarithmic depth

