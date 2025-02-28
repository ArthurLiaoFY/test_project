import salabim as sim

from product import SN


class Conveyor(sim.Component):
    def __init__(
        self,
        from_buffer: sim.Store | None,
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
        self.reset_remain_length(offset=0)
        self.reset_remain_time

    def reset_remain_length(self, offset: float):
        self.remain_length = self.conveyor_length + offset

    @property
    def reset_remain_time(self):
        self.remain_time = 1

    def process(self):
        while True:
            if self.from_buffer is None:
                while self.to_buffer.available_quantity() <= 0:
                    self.standby()
                product = SN(name="產品.")
            else:
                while len(self.from_buffer) == 0:
                    self.standby()
                product = self.from_store(self.from_buffer)

            production_complete = self.remain_length <= 0
            while not production_complete:
                if self.remain_length - self.conveyor_speed >= 0:
                    self.hold(min(1, self.remain_time))
                    self.remain_length -= self.conveyor_speed
                    offset = 0
                    self.reset_remain_time
                else:
                    self.hold(self.remain_length / self.conveyor_speed)
                    offset = self.remain_length - self.conveyor_speed
                    self.remain_time = 1 - self.remain_length / self.conveyor_speed
                    production_complete = True

            self.reset_remain_length(offset=offset)
            while self.to_buffer.available_quantity() <= 0:
                self.standby()
            self.to_store(self.to_buffer, product)

    def speed_accelerate(self, accelerate):
        self.conveyor_speed = max(
            min(self.conveyor_speed + accelerate, self.conveyor_max_speed),
            self.conveyor_min_speed,
        )
