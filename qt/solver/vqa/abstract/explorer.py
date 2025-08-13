from abc import ABC, abstractmethod

from .optimizer import Optimizer
from qt.utils import iprint
from qt.model import LinearConstrainedBinaryOptimization as LcboModel

from qt.circuit import CircuitOption
from qt.model import ModelOption
from . import VqaCircuit
from ..data_analyzer import DataAnalyzer
from ....provider import Provider
import time

class Explorer(ABC):
    def __init__(self, prb_model: LcboModel, optimizer: Optimizer):
        if isinstance(prb_model, LcboModel):
            self.model_option = prb_model.to_model_option()
        elif isinstance(prb_model, ModelOption):
            self.model_option = prb_model
        else:
            raise TypeError(f"Expected LcboModel or ModelOption, got {type(prb_model)}")
        self.optimizer: Optimizer = optimizer
        self.circuit_option: CircuitOption = None

        self._circuit = None
        self.original_provider: Provider = None
        self.explore_provider: Provider = None

        self.solver_start_time = time.perf_counter()  # 记录开始时间用于计算端到端时间


    @abstractmethod
    def explore(self):
        pass

    def explore_with_time(self):
        result = self.explore()
        solver_end_time = time.perf_counter()  # 使用 perf_counter 记录结束时间
        self.end_to_end_time = solver_end_time - self.solver_start_time
        # 同步给调用explorer的solver
        self.original_provider.quantum_circuit_execution_time = self.explore_provider.quantum_circuit_execution_time

        return result

    
    def time_analyze(self):
        quantum = self.circuit_option.provider.quantum_circuit_execution_time
        classcial = self.end_to_end_time - quantum
        return classcial, quantum
    
    def run_counts(self):
        return self.circuit_option.provider.run_count