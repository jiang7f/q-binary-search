import numpy as np
from qiskit import QuantumCircuit
from qt.provider import Provider
from qt.utils import iprint
from qt.utils.get_phase import get_phase
from qt.model import ModelOption
from .abstract import ExactCircuit, ExactSolver
from .option import QbsCircuitOption
from .module.rsg_plus import add_rsg_plus
from .module.obj import add_phase_obj
from qiskit.circuit.library import QFT

class QbsCircuit(ExactCircuit[QbsCircuitOption]):
    def __init__(self, circuit_option: QbsCircuitOption, model_option: ModelOption):
        super().__init__(circuit_option, model_option)
        self.inference_circuit = self.create_circuit()

    def inference(self):
        final_qc = self.inference_circuit
        counts = self.circuit_option.provider.get_counts_with_time(final_qc, shots=self.circuit_option.shots)
        collapse_state, probs = self.process_counts(counts)
        return collapse_state, probs
    
    def create_circuit(self) -> QuantumCircuit:
        num_qubits = self.model_option.num_qubits        
        mcx_mode = self.circuit_option.mcx_mode
        len_hd = len(self.model_option.Hd_bitstr_list)

        if self.circuit_option.repeat is None:
            repeat = num_qubits
        else:
            repeat = self.circuit_option.repeat

        if mcx_mode == "constant":
            qc = QuantumCircuit(num_qubits + 1 + repeat * len_hd + 2, num_qubits + 1)
            gate_qc = QuantumCircuit(num_qubits + 1 + repeat * len_hd)
            anc_idx = [num_qubits, num_qubits + 1]
            anc_v_to_w_idx = list(range(num_qubits + 1, num_qubits + 1 + repeat * len_hd))
            phase_estimate_idx = list(range(num_qubits + 1 + repeat * len_hd, num_qubits + 1 + repeat * len_hd + 2))
        elif mcx_mode == "linear":
            qc = QuantumCircuit(2 * num_qubits + repeat * len_hd, num_qubits + 1)
            gate_qc = QuantumCircuit(2 * num_qubits + repeat * len_hd + 2)
            anc_idx = list(range(num_qubits, 2 * num_qubits))
            anc_v_to_w_idx = list(range(2 * num_qubits, 2 * num_qubits + repeat * len_hd))
            phase_estimate_idx = list(range(2 * num_qubits + repeat * len_hd, 2 * num_qubits + repeat * len_hd + 2))

        qc = self.circuit_option.provider.transpile(qc)
        for i in np.nonzero(self.model_option.feasible_state)[0]:
            qc.x(i)
        
        
        Hd_bitstr_list = np.tile(self.model_option.Hd_bitstr_list, (repeat, 1))
        # 通过rsg_plus制备可行解近似均匀叠加态
        add_rsg_plus(qc, Hd_bitstr_list, anc_idx, mcx_mode, anc_v_to_w_idx)
        # 下面这个函数能对上述态产生一个相位，就是要估计的相位
        add_phase_obj(qc=gate_qc, scale=1, obj_dct=self.model_option.obj_dct, include_identity_term=True)


        u_gate = gate_qc.to_gate()
        cu_gate = u_gate.control(1)


        for repeat, i in enumerate(phase_estimate_idx[:-1]):
            qc.h(i)
            # u_power_gate = u_gate.power(2**repeat)
            for _ in range(2**repeat):
                qc.append(cu_gate, [i] + list(range(u_gate.num_qubits)))

        # qc.append(QFT(1, do_swaps=True).inverse().to_gate(), phase_estimate_idx[:-1])

        get_phase(qc, interested_bits=list(range(num_qubits)))
        exit()
        # get_phase(qc, interested_bits=list(range(num_qubits)))

        print(qc.draw())
        qc.measure(list(range(num_qubits)) + phase_estimate_idx[:-1], range(num_qubits + 1)[::-1])

        transpiled_qc = self.circuit_option.provider.transpile(qc)
        return transpiled_qc


class QbsSolver(ExactSolver):


    def __init__(
        self,
        *,
        prb_model,
        provider: Provider,
        shots: int = 1024,
        repeat: int = None,
        mcx_mode: str = "constant",
        eps: float = 1e-0
    ):
        super().__init__(prb_model)
        
        self.circuit_option = QbsCircuitOption(
            provider=provider,
            shots=shots,
            repeat=repeat,
            mcx_mode=mcx_mode,
        )
        self.eps = eps

    @property
    def circuit(self) -> QbsCircuit:
        if self._circuit is None:
            self._circuit = QbsCircuit(self.circuit_option, self.model_option)
        return self._circuit

    def check(self, mid):
        
        ''' 振幅放大后 有没有b '''
        if mid > 530:
            return True
        else:
            return False
        

    def _solve_impl(self):
        # 估计取值范围
        pass
        bound_left = 0
        bound_right = 10000
        print(self.circuit.inference())
        iprint("Starting binary search...")
        # binary search
        while bound_right - bound_left > self.eps:
            mid = (bound_left + bound_right) / 2
            iprint(f"Check: {mid}")
            if self.check(mid):
                bound_right = mid  # 缩小右边界，逼近最小满足条件的值
            else:
                bound_left = mid   # 舍弃当前和左边，逼近满足条件的区间
        
        # 得到最后一个b
        iprint(f"Optimal value found: {bound_left}")