from qiskit import QuantumCircuit
from typing import Iterable

def mcx_gate_decompose(qc: QuantumCircuit, list_controls:Iterable, qubit_target:int, list_ancilla:Iterable, mcx_mode):
    if mcx_mode == 'constant':
        # 自动分解，34 * 非零元
        qc.mcx(list_controls, qubit_target, list_ancilla[0], mode='recursion')
    elif mcx_mode == 'linear':
        # log 但是用更多比特，映射后可能反而更差
        mcx_n_anc_log_decompose(qc,list_controls, qubit_target, list_ancilla)
    else:
        qc.mcx(list_controls, qubit_target, list_ancilla[0])
        
# 用更多比特，对应cxmode为linear，拓扑可能更差
def mcx_n_anc_log_decompose(circuit: QuantumCircuit, control_qubits, target_qubit, ancillary_qubits):
    """
    This function implements the multi-controlled-X gate using the Toffoli gate.
    """
    if len(control_qubits) == 0:
        circuit.x(target_qubit)
    elif len(control_qubits) == 1:
        circuit.cx(control_qubits[0], target_qubit)
        return 0
    elif len(control_qubits) == 2:
        circuit.ccx(control_qubits[0], control_qubits[1], target_qubit)
        return 1
    else:
        circuit.ccx(control_qubits[0], control_qubits[1], ancillary_qubits[0])
        res = mcx_n_anc_log_decompose(
            circuit,
            control_qubits[2:] + [ancillary_qubits[0]],
            target_qubit,
            ancillary_qubits[1:],
        )
        circuit.ccx(control_qubits[0], control_qubits[1], ancillary_qubits[0])
        return res