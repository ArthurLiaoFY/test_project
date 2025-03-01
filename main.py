# %%
import json
from collections import defaultdict

import numpy as np
import salabim as sim

from agent.q_agent import Agent
from config import *
from digital_twins.conveyor import Conveyor
from digital_twins.machine import Machine

# %%
conveyor_agent = {
    "conveyor1_agent": Agent(**q_learn_kwargs),
    "conveyor2_agent": Agent(**q_learn_kwargs),
}


# %%
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

    def conveyor_1_reward(self, conveyor_state):
        # conveyor 1 loss, if head buffer is empty the conveyer length is loss else speed is loss
        return (
            -1
            * (
                2
                * (1 - conveyor_state.get("head_buffer_full"))
                * conveyor_state.get("conveyor1_remain_length")
                + conveyor_state.get("head_buffer_full")
                * conveyor_state.get("conveyor1_speed")
            )
            if not conveyor_state.get("pass_one_to_head_buffer")
            else 0
        )

    def conveyor_2_reward(self, conveyor_state):
        # conveyor 2 loss, if tail buffer is empty speed is loss else the conveyer length is loss
        return (
            -1
            * (
                2
                * (1 - conveyor_state.get("tail_buffer_full"))
                * conveyor_state.get("conveyor2_speed")
                + conveyor_state.get("tail_buffer_full")
                * conveyor_state.get("conveyor1_remain_length")
            )
            if not conveyor_state.get("pass_one_to_sink")
            else 0
        )

    def process(self) -> None:
        while True:
            # state
            conveyor_state = {
                "conveyor1_remain_length": conveyor1.remain_length,
                "conveyor1_speed": conveyor1.conveyor_speed,
                "head_buffer_full": head_buffer.available_quantity() == 0,
                "pass_one_to_head_buffer": False,
                "machine": round(machine.scheduled_time() - env.now(), 3),
                "tail_buffer_full": tail_buffer.available_quantity() == 0,
                "conveyor2_remain_length": conveyor2.remain_length,
                "conveyor2_speed": conveyor2.conveyor_speed,
                "pass_one_to_sink": False,
            }
            # action
            conveyor1_action_idx = conveyor_agent["conveyor1_agent"].select_action_idx(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k
                    not in (
                        "tail_buffer_full",
                        "conveyor2_remain_length",
                        "pass_one_to_head_buffer",
                        "pass_one_to_sink",
                    )
                )
            )

            conveyor2_action_idx = conveyor_agent["conveyor2_agent"].select_action_idx(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k
                    not in (
                        "head_buffer_full",
                        "conveyor1_remain_length",
                        "pass_one_to_head_buffer",
                        "pass_one_to_sink",
                    )
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

            self.scan_record[round(self.env.now(), 2)] = conveyor_state

            # wait until next scan
            self.hold(self.scan_interval)

            # reward
            conveyor_1_reward_history = self.conveyor_1_reward(
                conveyor_state=conveyor_state
            )
            conveyor_2_reward_history = self.conveyor_2_reward(
                conveyor_state=conveyor_state
            )

            # next state
            conveyor_new_state = {
                "conveyor1_remain_length": conveyor1.remain_length,
                "conveyor1_speed": conveyor1.conveyor_speed,
                "pass_one_to_head_buffer": (
                    True
                    if conveyor1.remain_length
                    - conveyor_state.get("conveyor1_remain_length")
                    > 0
                    else False
                ),
                "head_buffer_full": head_buffer.available_quantity() == 0,
                "machine": round(machine.scheduled_time() - self.env.now(), 3),
                "tail_buffer_full": tail_buffer.available_quantity() == 0,
                "conveyor2_remain_length": conveyor2.remain_length,
                "conveyor2_speed": conveyor2.conveyor_speed,
                "pass_one_to_sink": (
                    True
                    if conveyor2.remain_length
                    - conveyor_state.get("conveyor2_remain_length")
                    > 0
                    else False
                ),
            }
            # update policy
            conveyor_agent["conveyor1_agent"].update_policy(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k not in ("tail_buffer_full", "conveyor2_remain_length")
                ),
                action_idx=conveyor1_action_idx,
                reward=conveyor_1_reward_history,
                next_state_tuple=tuple(
                    v
                    for k, v in conveyor_new_state.items()
                    if k not in ("tail_buffer_full", "conveyor2_remain_length")
                ),
            )
            conveyor_agent["conveyor2_agent"].update_policy(
                state_tuple=tuple(
                    v
                    for k, v in conveyor_state.items()
                    if k not in ("head_buffer_full", "conveyor1_remain_length")
                ),
                action_idx=conveyor2_action_idx,
                reward=conveyor_2_reward_history,
                next_state_tuple=tuple(
                    v
                    for k, v in conveyor_new_state.items()
                    if k not in ("head_buffer_full", "conveyor1_remain_length")
                ),
            )


# %%


for episode in range(10000):
    env = sim.Environment(trace=True)

    head_buffer = sim.Store(name="前方緩存區", capacity=1, env=env)
    tail_buffer = sim.Store(name="後方緩存區", capacity=1, env=env)
    sn_sink = sim.Store(name="產品接收器", capacity=10000, env=env)

    conveyor1 = Conveyor(
        name="前方傳輸帶",
        from_buffer=None,
        to_buffer=head_buffer,
        conveyor_speed=conveyor_1_speed,
        conveyor_max_speed=conveyor_max_speed,
        conveyor_min_speed=conveyor_min_speed,
        scan_interval=conveyor_scan_interval,
        conveyor_length=conveyor1_length,
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
        conveyor_length=conveyor2_length,
        env=env,
    )

    env_scanner = EnvScanner(name="監視器", scan_interval=env_scan_interval, env=env)
    try:
        env.run(run_till)
        if episode == 0 or (episode > 5000 and episode % 50 == 1):
            print("episode : ", episode, ": ", len(sn_sink))
            conveyor1.status.print_histogram(values=True)
            machine.status.print_histogram(values=True)
            conveyor2.status.print_histogram(values=True)
    except ValueError:
        # if not dividable occur value error
        continue

    sim.reset()
    break

# %%
env_scanner.speed_accelerate_history
# %%
