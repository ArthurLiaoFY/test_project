import salabim as sim

from product import SN


class FirstConveyor(sim.Component):
    def __init__(
        self,
        to_buffer: sim.Store,
        conveyor_speed: float = 2.0,
        conveyor_max_speed: int = 5,
        conveyor_min_speed: int = 0,
        conveyor_length: float = 20.0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.to_buffer = to_buffer
        self.conveyor_speed = conveyor_speed
        self.conveyor_max_speed = conveyor_max_speed
        self.conveyor_min_speed = conveyor_min_speed
        self.conveyor_length = conveyor_length
        self.reset_remain_length

    @property
    def reset_remain_length(self):
        self.remain_length = self.conveyor_length

    def process(self):
        while True:
            while self.to_buffer.available_quantity() <= 0:
                self.standby()
            self.reset_remain_length
            product = SN(name="產品.")
            while self.remain_length > 0:
                if self.remain_length - self.conveyor_speed >= 0:
                    self.remain_length -= self.conveyor_speed
                    self.hold(1)
                else:
                    self.hold(self.remain_length / self.conveyor_speed)
                    self.remain_length = 0

            self.to_store(self.to_buffer, product)

    def speed_accelerate(self, accelerate):
        self.conveyor_speed = max(
            min(self.conveyor_speed + accelerate, self.conveyor_max_speed),
            self.conveyor_min_speed,
        )


class Conveyor(sim.Component):
    def __init__(
        self,
        from_buffer: sim.Store,
        to_buffer: sim.Store,
        conveyor_speed: float = 2.0,
        conveyor_max_speed: int = 5,
        conveyor_min_speed: int = 0,
        conveyor_length: float = 20.0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.from_buffer = from_buffer
        self.to_buffer = to_buffer
        self.conveyor_speed = conveyor_speed
        self.conveyor_max_speed = conveyor_max_speed
        self.conveyor_min_speed = conveyor_min_speed
        self.conveyor_length = conveyor_length
        self.reset_remain_length

    @property
    def reset_remain_length(self):
        self.remain_length = self.conveyor_length

    def process(self):
        while True:
            while len(self.from_buffer) == 0:
                self.standby()
            self.reset_remain_length
            product = self.from_store(self.from_buffer)
            while self.remain_length > 0:
                if self.remain_length - self.conveyor_speed >= 0:
                    self.remain_length -= self.conveyor_speed
                    self.hold(1)
                else:
                    self.hold(self.remain_length / self.conveyor_speed)
                    self.remain_length = 0
            while self.to_buffer.available_quantity() <= 0:
                self.standby()
            self.to_store(self.to_buffer, product)

    def speed_accelerate(self, accelerate):
        self.conveyor_speed = max(
            min(self.conveyor_speed + accelerate, self.conveyor_max_speed),
            self.conveyor_min_speed,
        )
