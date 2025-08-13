from abc import ABC, abstractmethod
from qt.utils import iprint
from qt.model import LinearConstrainedBinaryOptimization as LcboModel

from qt.circuit import CircuitOption
from qt.model import ModelOption
from . import ExactCircuit
import time

class ExactSolver(ABC):
    def __init__(self, prb_model: LcboModel):
        if isinstance(prb_model, LcboModel):
            self.model_option = prb_model.to_model_option()
        elif isinstance(prb_model, ModelOption):
            self.model_option = prb_model
        else:
            raise TypeError(f"Expected LcboModel or ModelOption, got {type(prb_model)}")
        
        self.circuit_option: CircuitOption = None
        self._circuit = None

        self.collapse_state_lst = None
        self.probs_lst = None

        self.solver_start_time = time.perf_counter()  # 记录开始时间用于计算端到端时间

    def solve(self):
        self._solve_impl()
        self._finalize_timing()

    @property
    @abstractmethod
    def circuit(self) -> ExactCircuit:
        pass

    @abstractmethod
    def _solve_impl(self):
        """子类实现具体的求解逻辑"""
        pass

    def _finalize_timing(self):
        solver_end_time = time.perf_counter()
        self.end_to_end_time = solver_end_time - self.solver_start_time

    def time_analyze(self):
        quantum = self.circuit_option.provider.quantum_circuit_execution_time
        classcial = self.end_to_end_time - quantum
        return classcial, quantum
    
    def circuit_analyze(self, metrics_lst):
        return self.circuit.analyze(metrics_lst)
    
