from qiskit import QuantumCircuit
from typing import Dict
from itertools import combinations

# e^itH的分解，映射目标函数到相位上,默认最前几位是变量比特
def add_phase_obj(qc: QuantumCircuit, scale: float, obj_dct: Dict, include_identity_term=False):
    """https://quantumcomputing.stackexchange.com/questions/5567/circuit-construction-for-hamiltonian-simulation"""
    # print(obj_dict)
    for pow, terms in obj_dct.items():
        for vars_tuple, coeff in terms:
            if include_identity_term:
                # 加上 Z^0 = I 的贡献（全局相位）
                theta_0 = scale * coeff / (2 ** pow)
                qc.global_phase += theta_0

            for k in range(1, pow + 1):
                # pi{j=0,j=n} (I-Z_j)/2 展开如下
                final_theta = scale * (1 / 2) ** pow * coeff * (-1) ** k
                for combo in combinations(range(pow), k):
                    for i in range(len(combo) - 1):
                        qc.cx(vars_tuple[combo[i]], vars_tuple[combo[i + 1]])
                    # Rz(θ)实现的是e^{-izθ/2}，因此需要乘以-2
                    qc.rz(-2 * final_theta, vars_tuple[combo[-1]])
                    for i in range(len(combo) - 2, -1, -1):
                        qc.cx(vars_tuple[combo[i]], vars_tuple[combo[i + 1]])