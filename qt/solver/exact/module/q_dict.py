from qiskit import QuantumCircuit
from typing import List, Dict
from itertools import combinations
from qiskit.circuit.library import QFT
import numpy as np
    
def add_q_dict(qc: QuantumCircuit, flact_idx: List, scale: float, obj_dct: Dict):
    num_flact = len(flact_idx)
    scaling = np.pi * 2 ** (1 - num_flact)
    qc.append(QFT(num_flact).to_gate(), flact_idx)
    # 把obj ancil转到y轴方向
    for pow, terms in obj_dct.items():
        if pow == 0:
            for _, coeff in terms:
                for i, q_i in enumerate(flact_idx):
                    qc.p(scaling * 2**i * coeff, q_i)
        else:
            for vars_tuple, coeff in terms:
                for i, q_i in enumerate(flact_idx):
                    qc.mcp(scaling * 2**i * coeff, vars_tuple, q_i) 
                # qc.barrier()

    qc.append(QFT(num_flact).inverse().to_gate(), flact_idx)


def add_q_dict_with_ancila(qc: QuantumCircuit, flact_idx: List, ancil_idx: List, scale: float, obj_dct: Dict):
    num_flact = len(flact_idx)
    qc.append(QFT(num_flact).to_gate(), flact_idx)
    # 把obj ancil转到y轴方向
    qc.h(ancil_idx[0])
    qc.s(ancil_idx[0])

    qc.sdg(ancil_idx[0])
    qc.h(ancil_idx[0])
    qc.append(QFT(num_flact).inverse().to_gate(), flact_idx)
    pass