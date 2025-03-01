# %%
import json
from collections import defaultdict

import numpy as np
import salabim as sim

from agent.q_agent import Agent
from config import q_learn_kwargs
from conveyor import Conveyor
from machine import Machine

# %%
run_till = 50  # 1 hour
seed = 1122
conveyor_1_speed = 5
conveyor_2_speed = 5
conveyor_max_speed = 10
conveyor_min_speed = 0
conveyor_scan_interval = 0.01
env_scan_interval = 1
machine_cycle_time = 3
# %%
env = sim.Environment(
    # trace=True if run_till <= 100 else False,
    trace=False,
    random_seed=seed,
)
env.total_count = 0
# %%

head_buffer = sim.Store(name="前方緩存區", capacity=1)
tail_buffer = sim.Store(name="後方緩存區", capacity=1)
sn_sink = sim.Store(name="產品接收器", capacity=10000)

conveyor1 = Conveyor(
    name="前方傳輸帶",
    from_buffer=None,
    to_buffer=head_buffer,
    conveyor_speed=conveyor_1_speed,
    conveyor_max_speed=conveyor_max_speed,
    conveyor_min_speed=conveyor_min_speed,
    scan_interval=conveyor_scan_interval,
    env=env,
)

machine = Machine(
    name="機器手臂",
    from_buffer=head_buffer,
    to_buffer=tail_buffer,
    machine_cycle_time=machine_cycle_time,
    env=env,
)

conveyor2 = Conveyor(
    name="後方傳輸帶",
    from_buffer=tail_buffer,
    to_buffer=sn_sink,
    conveyor_speed=conveyor_2_speed,
    conveyor_max_speed=conveyor_max_speed,
    conveyor_min_speed=conveyor_min_speed,
    scan_interval=conveyor_scan_interval,
    env=env,
)


conveyor_agent = {
    "conveyor1_agent": Agent(**q_learn_kwargs),
    "conveyor2_agent": Agent(**q_learn_kwargs),
}


class EnvScanner(sim.Component):
    def __init__(self, scan_interval: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scan_interval = scan_interval
        self.reset()

    def reset(self):
        self.scan_record = {}
        self.speed_accelerate_history = {
            "conveyor1": [],
            "conveyor2": [],
        }

    def reward(self):
        part1 = len(head_buffer) + len(tail_buffer)  # machine idle time
        part2 = 0
        part3 = 0
        part4 = 0
        return -1 * (part1 + part2 + part3 + part4)

    def process(self) -> None:
        while True:
            # state
            conveyor_state = {
                "conveyor1": round(conveyor1.remain_length, 2),
                "head_buffer_full": head_buffer.available_quantity() == 0,
                "machine": round(machine.scheduled_time() - env.now(), 3),
                "tail_buffer_full": tail_buffer.available_quantity() == 0,
                "conveyor2": round(conveyor2.remain_length, 2),
            }
            # action
            conveyor1_action_idx = conveyor_agent["conveyor1_agent"].select_action_idx(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k not in ("tail_buffer_full", "conveyor2")
                )
            )

            conveyor2_action_idx = conveyor_agent["conveyor2_agent"].select_action_idx(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k not in ("head_buffer_full", "conveyor1")
                )
            )

            # apply action
            accelerate1 = conveyor_agent["conveyor1_agent"].action_idx_to_action(
                conveyor1_action_idx
            )
            accelerate2 = conveyor_agent["conveyor2_agent"].action_idx_to_action(
                conveyor2_action_idx
            )
            conveyor1.speed_accelerate(accelerate=accelerate1)
            conveyor2.speed_accelerate(accelerate=accelerate2)
            self.speed_accelerate_history["conveyor1"].append(accelerate1)
            self.speed_accelerate_history["conveyor2"].append(accelerate2)

            self.scan_record[round(env.now(), 2)] = conveyor_state

            # wait until next scan
            self.hold(self.scan_interval)

            # reward
            reward = self.reward()

            # next state
            conveyor_new_state = {
                "conveyor1": round(conveyor1.remain_length, 2),
                "head_buffer_full": head_buffer.available_quantity() == 0,
                "machine": round(machine.scheduled_time() - env.now(), 3),
                "tail_buffer_full": tail_buffer.available_quantity() == 0,
                "conveyor2": round(conveyor2.remain_length, 2),
            }

            # update policy
            conveyor_agent["conveyor1_agent"].update_policy(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k not in ("tail_buffer_full", "conveyor2")
                ),
                action_idx=conveyor1_action_idx,
                reward=reward,
                next_state_tuple=tuple(
                    v
                    for k, v in conveyor_new_state.items()
                    if k not in ("tail_buffer_full", "conveyor2")
                ),
            )
            conveyor_agent["conveyor2_agent"].update_policy(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k not in ("head_buffer_full", "conveyor1")
                ),
                action_idx=conveyor2_action_idx,
                reward=reward,
                next_state_tuple=tuple(
                    v
                    for k, v in conveyor_new_state.items()
                    if k not in ("head_buffer_full", "conveyor1")
                ),
            )


env_scanner = EnvScanner(name="監視器", scan_interval=env_scan_interval)
env.run(run_till)
# %%
env_scanner.scan_record
# %%
env_scanner.speed_accelerate_history
# %%
