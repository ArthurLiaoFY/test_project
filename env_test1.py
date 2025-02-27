import salabim as sim

from conveyor import Conveyor, FirstConveyor
from machine import Machine
from product import SN

run_till = 3600  # 1 hour
seed = 1122

for conveyor_1_speed in [2, 5, 10, 20]:
    for conveyor_2_speed in [2, 5, 10, 20]:
        print(
            "head conveyor speed:",
            conveyor_1_speed,
            "tail conveyor speed:",
            conveyor_2_speed,
        )
        env = sim.Environment(
            trace=True if run_till <= 100 else False,
            random_seed=seed,
        )
        env.total_count = 0

        head_buffer = sim.Store(name="前方緩存區", capacity=1)
        tail_buffer = sim.Store(name="後方緩存區", capacity=1)
        sn_sink = sim.Store(name="產品接收器", capacity=100)

        conveyor1 = FirstConveyor(
            name="前方傳輸帶",
            to_buffer=head_buffer,
            conveyor_speed=conveyor_1_speed,
        )

        machine = Machine(
            name="機器手臂",
            from_buffer=head_buffer,
            to_buffer=tail_buffer,
        )

        conveyor2 = Conveyor(
            name="後方傳輸帶",
            from_buffer=tail_buffer,
            to_buffer=sn_sink,
            conveyor_speed=conveyor_2_speed,
        )

        env.run(run_till)

        print(len(sn_sink))
        # machine.status.print_histogram(values=True)
        # conveyor1.status.print_histogram(values=True)
        # conveyor2.status.print_histogram(values=True)
        print("####" * 50)
