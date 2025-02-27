# %%
import salabim as sim


class FirstConveyor(sim.Component):
    def __init__(
        self,
        to_buffer: sim.Store,
        conveyor_speed: int = 2,
        conveyor_length: int = 20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.to_buffer = to_buffer
        self.conveyor_speed = conveyor_speed
        self.conveyor_length = conveyor_length

    def process(self):
        while True:
            while self.to_buffer.available_quantity() <= 0:
                self.standby()
            product = SN(name="產品.")
            self.hold(self.conveyor_length / self.conveyor_speed)
            self.to_store(self.to_buffer, product)


class MiddleConveyor(sim.Component):
    def __init__(
        self,
        from_buffer: sim.Store,
        to_buffer: sim.Store,
        conveyor_speed: int = 2,
        conveyor_length: int = 20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.from_buffer = from_buffer
        self.to_buffer = to_buffer
        self.conveyor_speed = conveyor_speed
        self.conveyor_length = conveyor_length

    def process(self):
        while True:
            while (
                len(self.from_buffer) == 0 or self.to_buffer.available_quantity() <= 0
            ):
                self.standby()
            product = self.from_store(self.from_buffer)
            self.hold(self.conveyor_length / self.conveyor_speed)
            self.to_store(self.to_buffer, product)


class LastConveyor(sim.Component):
    def __init__(
        self,
        from_buffer: sim.Store,
        conveyor_speed: int = 2,
        conveyor_length: int = 20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.from_buffer = from_buffer
        self.conveyor_speed = conveyor_speed
        self.conveyor_length = conveyor_length

    def process(self):
        while True:
            while len(self.from_buffer) == 0:
                self.standby()
            product = self.from_store(self.from_buffer)
            self.hold(self.conveyor_length / self.conveyor_speed)
            env.total_count += 1


class SN(sim.Component):
    def process(self):
        pass


class Machine(sim.Component):
    def __init__(
        self,
        from_buffer: sim.Store,
        to_buffer: sim.Store,
        machine_cycle_time: int = 5,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.from_buffer = from_buffer
        self.to_buffer = to_buffer
        self.machine_cycle_time = machine_cycle_time

    def process(self):
        while True:
            while (
                len(self.from_buffer) == 0 or self.to_buffer.available_quantity() <= 0
            ):
                self.standby()
            product = self.from_store(self.from_buffer)
            self.hold(self.machine_cycle_time)
            self.to_store(self.to_buffer, product)


# run_till = 3600  # 1 hour
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

        conveyor2 = LastConveyor(
            name="後方傳輸帶",
            from_buffer=tail_buffer,
            conveyor_speed=conveyor_2_speed,
        )

        env.run(run_till)

        print(env.total_count)
        # machine.status.print_histogram(values=True)
        # conveyor1.status.print_histogram(values=True)
        # conveyor2.status.print_histogram(values=True)
        print("####" * 50)

# %%
