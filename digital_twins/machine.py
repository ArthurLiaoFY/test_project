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
        self.reset()

    def reset(self):
        self.machine_process_time = 0

    def process(self):
        while True:
            while len(self.from_buffer) == 0:
                self.standby()
            product = self.from_store(self.from_buffer)
            self.reset
            self.hold(self.machine_cycle_time)
            self.machine_process_time = self.env.now()
            while self.to_buffer.available_quantity() <= 0:
                self.standby()
            self.to_store(self.to_buffer, product)
