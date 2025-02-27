import salabim as sim

from product import SN


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


class Conveyor(sim.Component):
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
                len(self.from_buffer) == 0 and self.to_buffer.available_quantity() <= 0
            ):
                self.standby()
            product = self.from_store(self.from_buffer)
            self.hold(self.conveyor_length / self.conveyor_speed)
            self.to_store(self.to_buffer, product)
