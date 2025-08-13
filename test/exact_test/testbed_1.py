from qt.model import LinearConstrainedBinaryOptimization as LcboModel
from qt.solver.vqa.optimizer import CobylaOptimizer, AdamOptimizer
from qt.solver.exact import (
    QbsSolver
)
from qt.provider import (
    AerGpuProvider, AerProvider, FakeBrisbaneProvider, FakeKyivProvider, FakeTorinoProvider, DdsimProvider,
)

# model ----------------------------------------------
m = LcboModel() 
x = m.addVars(3, name="x")
m.setObjective(x[0] + x[1] + 2 * x[2], "max")
# m.addConstr(x[0] + x[1] + x[2] == 2)
# m.addConstr(x[0] + x[1] == 1)
# exit()
m.addConstr(x[0] + x[1] - x[2] == 1)
# m.addConstr(x[2] + x[3] - x[4] == 1)

print(m.lin_constr_mtx)
# exit()
# m.set_penalty_lambda(0)
print(m)
optimize = m.optimize()
print(f"optimize_cost: {optimize}\n\n")

# sovler ----------------------------------------------
opt = CobylaOptimizer(max_iter=100, save_address='cost_history')
aer = DdsimProvider()
gpu = AerGpuProvider()
fake = FakeBrisbaneProvider()
# opt = AdamOptimizer(max_iter=200)
solver = QbsSolver(
    prb_model=m,  # 问题模型
    # optimizer=opt,  # 优化器
    provider=aer,  # 提供器（backend + 配对 pass_mannager ）
    # num_layers=1,
    # mcx_mode="linear",
)
print(solver.circuit_analyze(['depth', 'width', 'culled_depth', 'num_one_qubit_gates']))
# print(solver.search())
result = solver.solve()
# eval = solver.evaluation()
# # print(result)
# print(eval)
# print(opt.cost_history)
