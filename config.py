q_learn_kwargs = {
    "action_mapping_dict": {0: 0, 1: -0.1, 2: 0.1},
    "learning_rate": 0.1,
    "explore_rate": 0.5,
    "learning_rate_min": 0.03,
    "explore_rate_min": 0.03,
    "learning_rate_decay": 0.999,
    "explore_rate_decay": 0.999,
    "discount_factor": 0.99,
    "fully_explore_step": 0,
}
run_till = 50
seed = 1122
conveyor_1_speed = 0.5
conveyor_2_speed = 0.5
conveyor1_length = 3
conveyor2_length = 2
conveyor_max_speed = 1
conveyor_min_speed = 0
conveyor_scan_interval = 0.033
env_scan_interval = 1
machine_cycle_time = 7