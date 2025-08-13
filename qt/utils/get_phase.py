import cmath
import numpy as np
from qiskit.quantum_info import Statevector, partial_trace
from collections import defaultdict

def get_phase(qc, interested_bits=None):
    """
    获取量子电路的基态幅度和相位，并按关心的比特分组统计概率
    :param qc: QuantumCircuit 对象
    :param interested_bits: 一个包含关心比特下标的列表，例如 [0, 1, 4]
    :return: None
    """
    # 获取量子电路的状态向量
    statevector = Statevector(qc)
    n = int(np.log2(len(statevector)))
    basis = [format(i, f'0{n}b') for i in range(len(statevector))]

    if interested_bits is None:
        interested_bits = list(range(n))

    prob_phase_dict = defaultdict(float)

    for i, amplitude in enumerate(statevector):
        r = abs(amplitude)
        theta = cmath.phase(amplitude)
        if r > 1e-10:
            key_bits = ''.join(basis[i][n - 1 - bit] for bit in interested_bits)  # 注意Qiskit是倒序的
            theta_rounded = round(theta, 6)  # 为了避免浮点误差，进行适当四舍五入
            key = (key_bits, theta_rounded)
            prob_phase_dict[key] += r**2

    for (key_bits, theta), prob in prob_phase_dict.items():
        print(f"|{key_bits}>: e^(i {theta:.4f}), prob = {prob:.4f}")

# def get_phase(qc):
#     """
#     获取量子电路的基态幅度和相位
#     :param qc: QuantumCircuit 对象
#     :return: None
#     """
#     # 获取量子电路的状态向量
#     statevector = Statevector(qc)
#     # statevector = partial_trace(statevector, [3, 4]).to_statevector()
#     # 获取基态标签
#     n = int(np.log2(len(statevector)))
#     basis = [format(i, f'0{n}b') for i in range(len(statevector))]
#     # 打印每个基态的幅度和相位
#     for i, amplitude in enumerate(statevector):
#         r = abs(amplitude)
#         theta = cmath.phase(amplitude)
#         if r > 1e-10:  # 过滤掉非常接近0的项
#             print(f"|{basis[i]}>: {r:.4f} * e^(i {theta:.4f})")
                