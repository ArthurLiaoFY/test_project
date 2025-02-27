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
        self.accelerate = 0

    @property
    def reset_remain_length(self):
        self.remain_length = self.conveyor_length

    @property
    def reset_accelerate(self):
        self.accelerate = 0

    def process(self):
        while True:
            while self.to_buffer.available_quantity() <= 0:
                self.standby()
            self.reset_remain_length
            self.reset_accelerate
            product = SN(name="產品.")
            while self.remain_length > 0:
                if self.remain_length - self.conveyor_speed >= 0:
                    self.hold(1)
                    self.remain_length -= self.conveyor_speed
                else:
                    self.hold(self.remain_length / self.conveyor_speed)
                    self.remain_length = 0
                self.conveyor_accelerate

            self.to_store(self.to_buffer, product)

    @property
    def conveyor_accelerate(self):
        self.conveyor_speed += self.accelerate


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
        self.accelerate = 0

    @property
    def reset_remain_length(self):
        self.remain_length = self.conveyor_length

    @property
    def reset_accelerate(self):
        self.accelerate = 0

    def process(self):
        while True:
            while (
                len(self.from_buffer) == 0 and self.to_buffer.available_quantity() <= 0
            ):
                self.standby()
            self.reset_remain_length
            self.reset_accelerate
            product = self.from_store(self.from_buffer)
            while self.remain_length > 0:
                if self.remain_length - self.conveyor_speed >= 0:
                    self.hold(1)
                    self.remain_length -= self.conveyor_speed
                else:
                    self.hold(self.remain_length / self.conveyor_speed)
                    self.remain_length = 0
                self.conveyor_accelerate

            self.to_store(self.to_buffer, product)

    @property
    def conveyor_accelerate(self):
        self.conveyor_speed += self.accelerate
