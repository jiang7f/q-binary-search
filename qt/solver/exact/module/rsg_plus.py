from qiskit import QuantumCircuit
from typing import Iterable
import numpy as np
from .mcx import mcx_gate_decompose
# from qto.utils.get_phase import get_phase

def decompose_phase_gate(qc: QuantumCircuit, list_qubits:list, list_ancilla:list, phase:float, mcx_mode) -> QuantumCircuit:
    """
    Decompose a phase gate into a series of controlled-phase gates.
    Args:
        qc
        list_qubits
        list_ancilla
        phase (float): the phase angle of the phase gate.
        mcx_mode (str): the type of ancillary qubits used in the controlled-phase gates.
            'constant': use a constant number of ancillary qubits for all controlled-phase gates.
            'linear': use a linear number of ancillary qubits to guarantee logarithmic depth.
    Returns:
        QuantumCircuit: the circuit that implements the decomposed phase gate.
    """
    num_qubits = len(list_qubits)
    if num_qubits == 1:
        qc.p(phase, list_qubits[0])
    elif num_qubits == 2:
        qc.cp(phase, list_qubits[0], list_qubits[1])
    else:
        # convert into the multi-cx gate 
        # partition qubits into two sets
        half_num_qubit = num_qubits // 2
        qr1 = list_qubits[:half_num_qubit]
        qr2 = list_qubits[half_num_qubit:]
        qc.rz(-phase/2, list_ancilla[0])
        # use ", mode='recursion'" without transpile will raise error 'unknown instruction: mcx_recursive'
        mcx_gate_decompose(qc, qr1, list_ancilla[0], list_ancilla[1:], mcx_mode)
        qc.rz(phase/2, list_ancilla[0])
        mcx_gate_decompose(qc, qr2, list_ancilla[0], list_ancilla[1:], mcx_mode)
        qc.rz(-phase/2, list_ancilla[0])
        mcx_gate_decompose(qc, qr1, list_ancilla[0], list_ancilla[1:], mcx_mode)
        qc.rz(phase/2, list_ancilla[0])
        mcx_gate_decompose(qc, qr2, list_ancilla[0], list_ancilla[1:], mcx_mode)


def apply_convert(qc: QuantumCircuit, list_qubits, bit_string):
    num_qubits = len(bit_string)
    for i in range(0, num_qubits - 1):
        qc.cx(list_qubits[i + 1], list_qubits[i])
        if bit_string[i] == bit_string[i + 1]:
            qc.x(list_qubits[i])
    qc.h(list_qubits[num_qubits - 1])

def apply_reverse(qc: QuantumCircuit, list_qubits, bit_string):
    num_qubits = len(bit_string)
    qc.h(list_qubits[num_qubits - 1])
    for i in range(num_qubits - 2, -1, -1):
        if bit_string[i] == bit_string[i + 1]:
            qc.x(list_qubits[i])
        qc.cx(list_qubits[i + 1], list_qubits[i])
      
# def rasengan_component(qc: QuantumCircuit, list_qubits:Iterable, list_ancilla:Iterable, bit_string:str, phase:float, mcx_mode:str='linear'):
#     # 把|v>转换成|w>
#     from qiskit.circuit.library import MCXGate
#     for i, v in enumerate(bit_string):
#         if v == 0:
#             qc.x(list_qubits[i])
#     qc.append(MCXGate(len(bit_string)), qargs=list_qubits + [list_ancilla[0]])

#     for i, v in enumerate(bit_string):
#         if v == 0:
#             qc.x(list_qubits[i])
#     for i in list_qubits:
#         qc.cx(list_ancilla[0], i)
#     # 解除纠缠 无法实现
#     # qc.h(list_ancilla[0])
#     # pass
#     qc.reset(list_ancilla[0])     

#     apply_convert(qc, list_qubits, bit_string)
#     qc.x(list_qubits[-1])
#     decompose_phase_gate(qc, list_qubits, list_ancilla, -phase, mcx_mode)
#     qc.x(list_qubits[-1])
#     decompose_phase_gate(qc, list_qubits, list_ancilla, phase, mcx_mode)
#     apply_reverse(qc, list_qubits, bit_string)

#     # 给|w>加相位 pi / 2
#     for i, v in enumerate(bit_string):
#         if v == 0:
#             qc.x(list_qubits[i])
#     decompose_phase_gate(qc, list_qubits, list_ancilla, np.pi / 2, mcx_mode)
#     for i, v in enumerate(bit_string):
#         if v == 0:
#             qc.x(list_qubits[i])
def rasengan_component(qc: QuantumCircuit, list_qubits:Iterable, list_ancilla:Iterable, bit_string:str, phase:float, mcx_mode:str='linear', anc_v_to_w_idx:int=None):
    # 把|v>转换成|w>
    from qiskit.circuit.library import MCXGate
    for i, v in enumerate(bit_string):
        if v == 0:
            qc.x(list_qubits[i])
    qc.append(MCXGate(len(bit_string)), qargs=list_qubits + [anc_v_to_w_idx])

    for i, v in enumerate(bit_string):
        if v == 0:
            qc.x(list_qubits[i])
    for i in list_qubits:
        qc.cx(anc_v_to_w_idx, i)

    apply_convert(qc, list_qubits, bit_string)
    qc.x(list_qubits[-1])
    decompose_phase_gate(qc, list_qubits, list_ancilla, -phase, mcx_mode)
    qc.x(list_qubits[-1])
    decompose_phase_gate(qc, list_qubits, list_ancilla, phase, mcx_mode)
    apply_reverse(qc, list_qubits, bit_string)

    # 给|w>加相位 pi / 2
    for i, v in enumerate(bit_string):
        if v == 0:
            qc.x(list_qubits[i])
    decompose_phase_gate(qc, list_qubits, list_ancilla, np.pi / 2, mcx_mode)
    for i, v in enumerate(bit_string):
        if v == 0:
            qc.x(list_qubits[i])


def add_rsg_plus(qc: QuantumCircuit, Hd_bitstr_list, anc_idx, mcx_mode, anc_v_to_w_idx):
    # for i in range(qc.num_qubits):
    #     qc.h(i)
    for idx, hdi_vct in enumerate(Hd_bitstr_list):
        nonzero_indices = np.nonzero(hdi_vct)[0].tolist()
        hdi_bitstr = [0 if x == -1 else 1 for x in hdi_vct if x != 0]
        rasengan_component(qc, nonzero_indices, anc_idx, hdi_bitstr, np.pi/4, mcx_mode, anc_v_to_w_idx[idx])