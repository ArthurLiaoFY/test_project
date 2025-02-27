# %%
import salabim as sim


class SNGenerator(sim.Component):
    def __init__(
        self,
        conveyor_speed: int = 20,
        conveyor_length: int = 20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.conveyor_speed = conveyor_speed
        self.conveyor_length = conveyor_length

    def process(self):
        while True:
            while head_buffer.available_quantity() <= 0:
                self.standby()

            self.request(conveyor1)
            self.hold(self.conveyor_length / self.conveyor_speed)
            self.release()
            SN(name="產品.").enter(head_buffer)


class SNSink(sim.Component):
    def __init__(
        self,
        conveyor_speed: int = 2,
        conveyor_length: int = 20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.conveyor_speed = conveyor_speed
        self.conveyor_length = conveyor_length

    def process(self):
        while True:
            while tail_buffer.available_quantity() == tail_buffer.capacity.value:
                self.standby()

            self.request(conveyor2)
            self.hold(self.conveyor_length / self.conveyor_speed)
            product = self.from_store(tail_buffer)
            self.release()
            product.passivate()
            env.total_prod_amount += 1


class SN(sim.Component):
    def process(self):
        while True:
            self.passivate()

    def animation_objects(self, id):
        """
        the way the component is determined by the id, specified in AnimateQueue
        'text' means just the name
        any other value represents the color
        """
        if id == "text":
            animate_text = sim.AnimateText(
                text=self.name(), textcolor="fg", text_anchor="nw"
            )
            return 15, 0, animate_text
        else:
            animate_rectangle = sim.AnimateRectangle(
                (
                    -20,
                    0,
                    20,
                    20,
                ),  # (x lower left, y lower left, x upper right, y upper right)
                text=self.name(),
                fillcolor=id,
                textcolor="white",
                arg=self,
            )
            return 0, 30, animate_rectangle


class Machine(sim.Component):
    def __init__(
        self,
        machine_cycle_time: int = 5,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.machine_cycle_time = machine_cycle_time

    def process(self):
        while True:
            while len(head_buffer) == 0:
                self.standby()
            product = self.from_store(head_buffer)

            self.hold(self.machine_cycle_time)

            while tail_buffer.available_quantity() <= 0:
                self.standby()

            self.to_store(tail_buffer, product)


severity = "0"
animate = False
# run_till = 3600  # 1 hour
run_till = 100  # 1 hour
seed = 1122


if animate:
    env = sim.Environment(trace=False, random_seed=seed)
    env.background_color("40%gray")

    sim.AnimateImage("./digital_twins/factory-machine.png", x=350, y=400, width=300)
    sim.AnimateImage("./digital_twins/delivery-box.png", x=100, y=400, width=200)
    sim.AnimateImage("./digital_twins/delivery-box.png", x=700, y=400, width=200)

else:
    env = sim.Environment(
        trace=True if run_till <= 100 else False,
        random_seed=seed,
    )


env.total_prod_amount = 0

sn_generator = SNGenerator(name="產品發射器")
conveyor1 = sim.Resource("前方傳輸帶")
head_buffer = sim.Store(name="前方緩存區", capacity=1)
machine = Machine(name="機器手臂")
tail_buffer = sim.Store(name="後方緩存區", capacity=1)
conveyor2 = sim.Resource("後方傳輸帶")
sn_sink = SNSink(name="產品接收器")
if animate:
    hb_animate = sim.AnimateQueue(
        head_buffer,
        x=160,
        y=350,
        title="Head Buffer",
        direction="s",
        id="blue",
        titlefontsize=30,
    )
    tb_animate = sim.AnimateQueue(
        tail_buffer,
        x=760,
        y=350,
        title="Tail Buffer",
        direction="s",
        id="black",
        titlefontsize=30,
    )

env.animate(animate)
env.run(run_till)

# %%
machine.status.print_histogram(values=True)

# %%
print(env.total_prod_amount)
# %%
sn_generator.status.print_histogram(values=True)

# %%
sn_sink.status.print_histogram(values=True)

# %%
