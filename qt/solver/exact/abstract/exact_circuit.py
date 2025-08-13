from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Generic, TypeVar
from qt.circuit import Circuit, T, CircuitOption
from qt.model import ModelOption
from qiskit_ibm_runtime.fake_provider import FakeKyoto, FakeKyiv, FakeQuebec, FakeAlmadenV2, FakeBelemV2, FakeSantiagoV2

class ExactCircuit(Circuit[T], ABC):
    def __init__(self, circuit_option: T, model_option: ModelOption):
        super().__init__(circuit_option, model_option)

    def process_counts(self, counts: Dict) -> Tuple[List[List[int]], List[float]]:
        # collapse_state = [[int(char) for char in state] for state in counts.keys()]
        collapse_state = []
        for state in counts.keys():
            if ' ' in state:
                # 多个 ClassicalRegister，按空格拆分
                parts = state.split(' ')[::-1]
                collapse_state.append([int(b) for part in parts for b in part])
                # collapse_state.append([[int(b) for b in part] for part in parts])
            else:
                # 只有一个 ClassicalRegister，正常处理
                collapse_state.append([int(b) for b in state])
        # collapse_state = [[int(char) for char in state.replace(" ", "")] for state in counts.keys()]
        total_count = sum(counts.values())
        probs = [count / total_count for count in counts.values()]
        return collapse_state, probs