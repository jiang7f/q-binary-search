import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qt.provider import Provider
from qt.utils import iprint
from qt.utils.get_phase import get_phase
from qt.model import ModelOption
from .abstract import ExactCircuit, ExactSolver
from .option import QbsCircuitOption
from .module.rsg_plus import add_rsg_plus
from .module.obj import add_phase_obj
from .module.q_dict import add_q_dict
import math

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

        precision = 3

        # register 
        # qubits used in problem variables
        variables_qrgst = QuantumRegister(num_qubits, name="rasengan")
        # ancilla qubits used in MCX
        if mcx_mode == "constant":
            mcx_ancil_qrgst = QuantumRegister(1, name="mcx_ancil")
        elif mcx_mode == "linear":
            mcx_ancil_qrgst = QuantumRegister(num_qubits, name="mcx_ancil")
        # ancilla qubits used in rasengan plus
        rasg_ancil_qrgst = QuantumRegister(repeat * len_hd, name="rasg_ancil")
        # flag
        flag_qrgst = QuantumRegister(1, name="flag")
        # flact to objective value
        obj_qrgst = QuantumRegister(precision, name="obj")
        # quantum dict ancila
        # obj_ancil_qrgst = QuantumRegister(1, name="obj_ancil")
        # problem variables readout register
        variables_crgst = ClassicalRegister(num_qubits, name="cr_variables")
        obj_crgst = ClassicalRegister(precision, name="cr_obj")


        
        qc = QuantumCircuit(variables_qrgst, 
                            mcx_ancil_qrgst, 
                            rasg_ancil_qrgst, 
                            # obj_qrgst, 
                            # obj_ancil_qrgst,
                            )
        # qubit index
        current_qidx = 0
        variables_qidx = list(range(current_qidx, current_qidx + variables_qrgst.size))
        current_qidx += num_qubits
        mcx_ancil_qidx = list(range(current_qidx, current_qidx + mcx_ancil_qrgst.size))
        current_qidx += mcx_ancil_qrgst.size
        anc_v_to_w_qidx = list(range(current_qidx, current_qidx + rasg_ancil_qrgst.size))
        current_qidx += rasg_ancil_qrgst.size
        obj_qidx = list(range(current_qidx, current_qidx + obj_qrgst.size))
        current_qidx += obj_qrgst.size
        # obj_ancil_qidx = list(range(current_qidx, current_qidx + obj_ancil_qrgst.size))
        # current_qidx += obj_ancil_qrgst.size
        flag_qidx = list(range(current_qidx, current_qidx + flag_qrgst.size))
        current_qidx += flag_qrgst.size

        current_cidx = 0
        variables_cidx = list(range(current_cidx, current_cidx + variables_crgst.size))
        current_cidx += variables_crgst.size
        obj_cidx = list(range(current_cidx, current_cidx + obj_crgst.size))
        self.obj_cidx = obj_cidx
        current_cidx += obj_crgst.size


        qc = self.circuit_option.provider.transpile(qc)
        for i in np.nonzero(self.model_option.feasible_state)[0]:
            qc.x(i)
        
        Hd_bitstr_list = np.tile(self.model_option.Hd_bitstr_list, (repeat, 1))
        # 通过rsg_plus制备可行解近似均匀叠加态
        add_rsg_plus(qc, Hd_bitstr_list, mcx_ancil_qidx, mcx_mode, anc_v_to_w_qidx)
        # qc.barrier(label="rasengan_plus")
        # 把目标函数值映射到相位上
        # add_phase_obj(qc=qc, scale=1, obj_dct=self.model_option.obj_dct, include_identity_term=True)
        # get_phase(qc, interested_bits=variables_qidx)
        state_preparation = qc.to_gate()
        inver_state_preparation = state_preparation.inverse()
        # print(state_preparation.size)
        qc = QuantumCircuit(variables_qrgst, 
                            mcx_ancil_qrgst, 
                            rasg_ancil_qrgst, 
                            # obj_qrgst, 
                            # obj_ancil_qrgst,
                            )
        qc.add_register(obj_qrgst)
        preparation_qidx = variables_qidx + mcx_ancil_qidx + anc_v_to_w_qidx
        qc.append(state_preparation, preparation_qidx)
        qc.barrier()

        dict_qc = QuantumCircuit(variables_qrgst, 
                            mcx_ancil_qrgst, 
                            rasg_ancil_qrgst, 
                            obj_qrgst, 
                            # obj_ancil_qrgst,
                            )
        add_q_dict(dict_qc, flact_idx=obj_qidx, scale=1, obj_dct=self.model_option.obj_dct)
        dict_qc_gate = dict_qc.to_gate()
        inverse_dict_qc_gate = dict_qc_gate.inverse()
        qc.add_register(flag_qrgst)

        # qc.append(dict_qc_gate, preparation_qidx + obj_qidx)
        power = 1
        for _ in range(power):
            qc.append(dict_qc_gate, preparation_qidx + obj_qidx)
            qc.cx(obj_qidx[-1], flag_qidx[0])  # 让第一个量子比特的相位为pi
            qc.z(flag_qidx[0])
            qc.append(inverse_dict_qc_gate, preparation_qidx + obj_qidx)

            qc.barrier()
            qc.append(inver_state_preparation, preparation_qidx)
            diff_idx = preparation_qidx
            qc.x(diff_idx)
            qc.h(diff_idx[-1])
            if len(diff_idx) > 1:
                qc.mcx(diff_idx[:-1], diff_idx[-1])
            else:
                qc.z(diff_idx[0])
            qc.h(diff_idx[-1])
            qc.x(diff_idx)
            qc.append(state_preparation, preparation_qidx)
            qc.barrier()

        qc.add_register(variables_crgst, obj_crgst)
        # exit()
        qc.measure(variables_qidx + obj_qidx, variables_cidx[::-1] + obj_cidx)
        transpiled_qc = self.circuit_option.provider.transpile(qc)
        print(qc.draw())
        return transpiled_qc

    def is_good_state(self):
        def check_good_state(measurement):
            """Check whether ``measurement`` is a good state or not."""
            return measurement[self.obj_cidx[0]] == 1
        return check_good_state

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
        inference = self.circuit.inference()
        print(inference)
        func = self.circuit.is_good_state()
        for inf in inference[0]:
            print(inf, func(inf))
        iprint("Starting binary search...")
        # binary search
        
        # b
        threshold = 1
        optimum_value = math.inf
        optimum_key = math.inf
        n_key = 1 # self._num_key_qubits
        keys_measured = []
        self._n_iterations = 1000
        
        # Variables for stopping if we've hit the rotation max.
        rotations = 0
        max_rotations = int(np.ceil(100 * np.pi / 4))

        # optimum_found = False
        # while not optimum_found:
        #     m = 1
        #     improvement_found = False
        #     loops_with_no_improvement = 0
        #     while not improvement_found:
        #         loops_with_no_improvement += 1
        #         rotation_count = np.random.Generator.integers(0, m)
        #         rotations += rotation_count
        #         qc = self.circuit
        #         inference = self.circuit.inference()
        #         k = 0
        #         v = 0
        #         int_v = v + threshold
        #         if int_v < optimum_value:
        #             optimum_key = k
        #             optimum_value = int_v
        #             improvement_found = True
        #             # 要改这个
        #             threshold = optimum_value

        #         else:
        #             # Using Durr and Hoyer method, increase m.
        #             m = int(np.ceil(min(m * 8 / 7, 2 ** (n_key / 2))))

        #             # Check if we've already seen this value.
        #             if k not in keys_measured:
        #                 keys_measured.append(k)

        #             # Assume the optimal if any of the stop parameters are true.
        #             if (
        #                 loops_with_no_improvement >= self._n_iterations
        #                 # or len(keys_measured) == num_solutions
        #                 or rotations >= max_rotations
        #             ):
        #                 improvement_found = True
        #                 optimum_found = True

                # Track the operation count.
                # operations = circuit.count_ops()
                # operation_count[iteration] = operations
                # iteration += 1
                # logger.info("Operation Count: %s\n", operations)



        while bound_right - bound_left > self.eps:
            mid = (bound_left + bound_right) / 2
            iprint(f"Check: {mid}")
            if self.check(mid):
                bound_right = mid  # 缩小右边界，逼近最小满足条件的值
            else:
                bound_left = mid   # 舍弃当前和左边，逼近满足条件的区间
        
        # 得到最后一个b
        iprint(f"Optimal value found: {bound_left}")