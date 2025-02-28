# %%
from collections import defaultdict

import numpy as np
import salabim as sim

from conveyor import Conveyor
from machine import Machine

run_till = 50  # 1 hour
seed = 1122
conveyor_1_speed = 4
conveyor_2_speed = 4
scan_interval = 0.1

env = sim.Environment(
    # trace=True if run_till <= 100 else False,
    trace=False,
    random_seed=seed,
)
env.total_count = 0


head_buffer = sim.Store(name="前方緩存區", capacity=1)
tail_buffer = sim.Store(name="後方緩存區", capacity=1)
sn_sink = sim.Store(name="產品接收器", capacity=10000)

conveyor1 = Conveyor(
    name="前方傳輸帶",
    from_buffer=None,
    to_buffer=head_buffer,
    conveyor_speed=conveyor_1_speed,
    scan_interval=scan_interval,
    env=env,
)

machine = Machine(
    name="機器手臂",
    from_buffer=head_buffer,
    to_buffer=tail_buffer,
    machine_cycle_time=2.83,
    env=env,
)

conveyor2 = Conveyor(
    name="後方傳輸帶",
    from_buffer=tail_buffer,
    to_buffer=sn_sink,
    conveyor_speed=conveyor_2_speed,
    scan_interval=scan_interval,
    env=env,
)

l = {}


class EnvScanner(sim.Component):
    def __init__(self, scan_interval: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scan_interval = scan_interval
        self.reset()

    def reset(self) -> None:
        self.conveyor_speed_dict = defaultdict(list)

    def reward(self):
        part1 = len(head_buffer) + len(tail_buffer)  # machine idle time
        part2 = 0
        part3 = 0
        part4 = 0
        return -1 * (part1 + part2 + part3 + part4)

    def process(self) -> None:
        while True:

            # wait until next scan
            l[round(env.now(), 2)] = {
                "c1": round(conveyor1.remain_length, 2),
                "c1_s": round(conveyor1.conveyor_speed, 2),
                "m": round(machine.scheduled_time() -env.now(), 3),
                "c2": round(conveyor2.remain_length, 2),
                # "of": round(conveyor1.offset, 2),
                # "c1_rt": round(conveyor1.remain_time, 2),
                # "c1_rl": round(conveyor1.remain_length, 2),
                # "c2_status": conveyor2.status(),
            }
            # conveyor1.speed_accelerate(accelerate=0.3)

            self.hold(self.scan_interval)


env_scanner = EnvScanner(name="監視器", scan_interval=scan_interval)
env.run(run_till)

# %%
l
# %%
