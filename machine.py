import salabim as sim


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
            self.enter(self.to_buffer, product)
