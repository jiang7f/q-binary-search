from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Generic, TypeVar
from qt.circuit import Circuit, T, CircuitOption
from qt.model import ModelOption
from qiskit_ibm_runtime.fake_provider import FakeKyoto, FakeKyiv, FakeQuebec, FakeAlmadenV2, FakeBelemV2, FakeSantiagoV2

class VqaCircuit(Circuit[T], ABC):
    def __init__(self, circuit_option: T, model_option: ModelOption):
        super().__init__(circuit_option, model_option)

    @abstractmethod
    def get_num_params(self):
        pass

    def get_circuit_cost_func(self):
        def circuit_cost_func(params):
            collapse_state, probs = self.inference(params)
            costs = 0
            for value, prob in zip(collapse_state, probs):
                costs += self.model_option.obj_func(value) * prob
            return costs

        return circuit_cost_func