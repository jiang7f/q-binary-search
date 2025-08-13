should_print = True

from qt.problems.facility_location_problem import generate_flp
from qt.problems.set_cover_problem import generate_scp
from qt.problems.k_partition_problem import generate_kpp
from qt.problems.graph_coloring_problem import generate_gcp
from qt.model import LinearConstrainedBinaryOptimization as LcboModel
from qt.solver.vqa.optimizer import CobylaOptimizer, AdamOptimizer
from qt.solver.vqa import (
    HeaSolver, PenaltySolver, CyclicSolver, ChocoSolver, RasenganSolver,
)
from qt.provider import (
    AerGpuProvider, AerProvider, FakeBrisbaneProvider, FakeKyivProvider, FakeTorinoProvider, DdsimProvider,
)
from qt.solver.vqa.explorer import QtoExplorer
num_case = 1
# a, b = generate_scp(num_case,[(3, 3)])
a, b = generate_scp(num_case,[(5, 5)])
# print(a[0][0])
# (1, [(2, 1), (3, 2), (3, 3), (4, 3), (4, 4)], 1, 20)

print(b)

best_lst = []
arg_lst = []

for i in range(num_case):
    opt = CobylaOptimizer(max_iter=200)
    aer = DdsimProvider()
    a[0][i].set_penalty_lambda(400)
    explorer = QtoExplorer(
        prb_model=a[0][i],  # 问题模型
        optimizer=opt,  # 优化器
        provider=aer,  # 提供器（backend + 配对 pass_mannager ）
        num_layers=1,
        shots=1024,
        # mcx_mode="linear",
    )

    num_basis_lists, set_basis_lists, depth_lists = explorer.explore_with_time()
    print(num_basis_lists, depth_lists)
