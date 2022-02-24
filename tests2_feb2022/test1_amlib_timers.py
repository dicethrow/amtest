import sys, os
from termcolor import cprint
from typing import List
import textwrap

from amaranth import Elaboratable, Module, Signal, Mux, ClockSignal, ClockDomain, ResetSignal, Cat, Const
from amaranth.hdl.ast import Rose, Stable, Fell, Past
from amaranth.hdl.rec import DIR_NONE, DIR_FANOUT, DIR_FANIN, Layout, Record
from amaranth.hdl.mem import Memory
from amaranth.hdl.xfrm import DomainRenamer
from amaranth.cli import main_parser, main_runner
from amaranth.sim import Simulator, Delay, Tick, Passive, Active
from amaranth.asserts import Assert, Assume, Cover, Past
from amaranth.lib.fifo import AsyncFIFOBuffered
#from amaranth.lib.cdc import AsyncFFSynchronizer
from amaranth.lib.cdc import FFSynchronizer
from amaranth.build import Platform


from amlib.io import SPIRegisterInterface, SPIDeviceBus, SPIMultiplexer
from amlib.debug.ila import SyncSerialILA
# from amlib.utils.cdc import synchronize
from amlib.utils import Timer


from amtest.boards.ulx3s.common.upload import platform, UploadBase
from amtest.boards.ulx3s.common.clks import add_clock


# sys.path.append(os.path.join(os.getcwd(), "tests/ulx3s_gui_test/common"))
# from test_common import fpga_gui_interface, fpga_mcu_interface
# addrs = fpga_mcu_interface.register_addresses

class timerTest(Elaboratable):
	ui_layout = [
		("start",	1,	DIR_FANOUT),
		("done",	1,	DIR_FANIN),
		("active",	1,	DIR_FANIN)
	]

	debug_layout = [
		("count",	32,	DIR_FANIN)
	]

	def __init__(self, load):
		super().__init__()
		self.ui = Record(timerTest.ui_layout)
		self.debug = Record(timerTest.debug_layout)
		self.load = int(load)

	def elaborate(self, platform: Platform) -> Module:
		m = Module()

		ui = Record.like(self.ui)
		debug = Record.like(self.debug)
		m.d.sync += [
			self.ui.connect(ui),
			self.debug.connect(debug)
		]

		m.submodules.delayer = delayer = Timer(load=self.load)

		m.d.sync += [
			delayer.start.eq(ui.start),
			ui.done.eq(delayer.done),
			debug.count.eq(delayer.counter_out),
			ui.active.eq(delayer.counter_out != self.load)
		]

		return m

if __name__ == "__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	class Testbench(Elaboratable):
		timerTest_test_interface_layout = [
			("reset",			1, DIR_FANOUT), # note - this doesn't seem to show in traces, but still works?
			# ("leds", 			8, DIR_FANOUT) # can't do reset-less here, so using a separate signal
		] + timerTest.ui_layout

		
		def __init__(self):
			super().__init__()
			self.ui = Record(Testbench.timerTest_test_interface_layout)
			self.leds = Signal(8, reset_less=True)

		def elaborate(self, platform = None):
			m = Module()

			m.submodules.dut = dut = DomainRenamer("sync_1e6")(timerTest(load = 1e2 if platform == None else 1e6))

			ui = Record.like(self.ui)
			debug = Record.like(dut.debug)
			m.d.sync_1e6 += [
				self.ui.connect(ui),
				ui.connect(dut.ui, exclude=["reset"]),
				debug.connect(dut.debug)
			]

			# change a led flag each time one of these rises, so we can see quick changes
			# for i, each in enumerate([ui.start, ui.done, ui.reset, ui.active]):
			# 	with m.If(Rose(each)):
			# 		m.d.sync += self.leds[i].eq(~self.leds[i])
			m.d.sync_1e6 += self.leds.eq(debug.count[15:])

			def init_clocks():	
				# add slower clock for counters (i.e. so they don't limit speed)					
				m.d.sync += ResetSignal("sync").eq(ui.reset)
				m.d.sync_1e6 += ResetSignal("sync_1e6").eq(ui.reset)

			
			init_clocks()

			return m

	if args.action == "generate":
		# This is called 'formal verification'
		# where the simulator tests all conditions (within specified limits) that:
		# 	- are universally true (asserts). If a fail occurs, then show an example waveform.
		# 	- are valid for some condition (cover). Show a waveform that matches these.
		#		Note that the use of m.If() focusses the states of the cover below uses.
		# 	- match some assumptions.(Assume) This may be good to remove some illegal states.
		#	  Reduces the input
		# main_runner generates the output that will be run through yosys

		with open(current_filename+".sby", "w") as sby_file:
			file_content = f"""
			[tasks]
			cover
			bmc

			[options]
			bmc: mode bmc
			cover: mode cover
			depth 2
			multiclock off

			[engines]
			smtbmc boolector

			[script]
			read_ilang {__file__.replace(".py", "_toplevel.il")}
			prep -top top

			[files]
			{__file__.replace(".py", "_toplevel.il")}
			"""
			# [1:] removes first newline
			sby_file.write(textwrap.dedent(file_content[1:]))  

		class Adder(Elaboratable):
			def __init__(self):
				self.x = Signal(8)
				self.y = Signal(8)
				self.out = Signal(8)

			def elaborate(self, platform: Platform) -> Module:
				m = Module()

				# this is where the logic behavior is defined
				m.d.comb += self.out.eq(self.x + self.y)	# comb
				# m.d.sync += self.out.eq(self.x + self.y)	# sync

				return m 

			def ports(self) -> List[Signal]: # RobertBaruch recommends this
				return [self.x, self.y, self.out] # the ports?
		

		
		m = Module()
		m.submodules.adder = adder = Adder()



		# try formal verification
		m.d.comb += Assert(adder.out == (2*adder.x + adder.y)[:8]) 

		# # assume certain things, can be good to exclude illegal states
		# # this will reduce the 'input set' that are tried by cover and assert?
		m.d.comb += Assume(adder.x == (adder.y << 1)) 

		with m.If(adder.x == (adder.y << 1)):
			m.d.comb += Cover((adder.out > 0x00) & (adder.out < 0x40))
		
		# m.d.comb += Cover(adder.out == 0xFF) 	
		# m.d.comb += Cover((adder.out == 0x00) & (adder.x == 0xFE))


		main_runner(parser, args, m, ports=[] + adder.ports()) 



	elif args.action == "simulate":

		class Simulate(Elaboratable):
			def __init__(self):
				super().__init__()
				self.ui = Record(Testbench.timerTest_test_interface_layout)

			def timer_test(self):
				def strobe(signal):
					for _ in range(2):
						prev_value = yield signal
						yield signal.eq(~prev_value)
						yield
				yield Active()

				for repeat in range(3):

					yield Delay(1e-6) # delay at start

					yield from strobe(self.ui.start)

					while not (yield self.ui.done):
						yield

					# yield Delay(100e-6)

					yield Delay(1e-6) # delay at end

					# now do a reset
					
					yield from strobe(self.ui.reset)
					# yield from strobe(ClockSignal().rst)


			def elaborate(self, platform = None):
				m = Module()

				add_clock(m, "sync_1e6")
				add_clock(m, "sync")

				m.submodules.tb = tb = Testbench()
				ui = Record.like(self.ui)
				m.d.sync_1e6 += [
					self.ui.connect(ui),
					ui.connect(tb.ui, exclude=["reset"])
				]

				# m.domains.sync = cd_sync = ClockDomain("sync")
				# m.d.sync += cd_sync.rst.eq(ui.reset)
				
				return m

		# dut = Simulate_test()

		

		# m = Module()
		# m.submodules.dut = dut = Testbench()
		# dut_test_io = Record(Testbench.timerTest_test_interface_layout)
		# m.d.sync += dut_test_io.connect(dut.dut_test_io)
		# # dut.dut_test_io.connect(dut_test_io)

		top = Simulate()
		sim = Simulator(top)
		sim.add_clock(1/25e6, domain="sync")
		sim.add_sync_process(top.timer_test, domain="sync_1e6")

		with sim.write_vcd(
			f"{current_filename}_simulate.vcd",
			f"{current_filename}_simulate.gtkw",
			# traces=[
			# 	dut_test_io.trigger,
			# 	dut_test_io.done,
			# 	dut_test_io.reset,
			# 	cd_sync.rst,
			# 	dut_test_io.leds,
			# ] + dut.ports()	
			):
			sim.run()

	else: # upload - is there a test we could upload and do on the ulx3s?
		class Upload(UploadBase):
			def __init__(self):
				super().__init__()
				
			def elaborate(self, platform = None):
				m = super().elaborate(platform)

				m.submodules.tb = tb = Testbench()	

				ui = Record.like(tb.ui)
				m.d.sync_1e6 += ui.connect(tb.ui)

				start = Signal.like(ui.start)
				reset = Signal.like(ui.reset)
				m.d.sync_1e6 += [
					start.eq(self.i_buttons.left),
					ui.start.eq(Rose(start, domain="sync_1e6")),

					reset.eq(self.i_buttons.right),
					ui.reset.eq(Rose(reset, domain="sync_1e6")),

					self.leds.eq(tb.leds),
				]

				return m


		platform.build(Upload(), do_program=False, build_dir=f"{current_filename}_build")

