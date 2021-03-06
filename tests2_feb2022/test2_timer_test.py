import sys, os
from termcolor import cprint

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

import numpy as np

# new structure idea!
# or: instead of this, just have single-use timers?
# so they have fixed durations etc... may be less 
# routing delay, and better performance?
# ---
# or - just go with the set_timer_clocks() approach
# for now, as it would use a bus approach, which might
# be easier

# @staticmethod
# def delay_for_time():
# 	""" 
# 	usage idea:
# 	return a done signal so the following would work:

# 	...
# 	with m.If(delayer1.delay_for_time(4e-6))
# 		m.next = "REQUEST_REFRESH_SOON"
# 	...

# 	"""

# 	with m.FSM(name="delay_for_time_fsm"):
# 		# with m.State("")
# 		pass
	

# # new structure idea!
# @staticmethod
# def delay_for_clks():
# 	pass


class duration_timer(Elaboratable):
	""" 
	This assumes that the sync domain is used.
	Designed to be used with domainRenamer().
	"""
	ui_layout = [
		("start",	1,	DIR_FANOUT),
		("done",	1,	DIR_FANIN),
		("active",	1,	DIR_FANIN)
	]

	# debug_layout = [
	# 	("count",	32,	DIR_FANIN)
	# ]

	def __init__(self, *, clk_freq = None, clks_adjust = 0):
		super().__init__()
		if clk_freq != None:
			self.set_clk_freq(clk_freq)
		self.set_clks_adjust(clks_adjust)
		
	def set_clks_adjust(self, adjust):
		self.clks_adjust = adjust

	def set_clk_freq(self, freq):
		self.clk_freq = freq

	@staticmethod
	def delay_for_time(m, ui, delay):
		# ensure that at least the necessary clocks are delayed
		
		clks = int(np.ceil(delay/self.clk_freq))
		return duration_timer.delay_for_clocks(m, ui, clks)

	@staticmethod
	def delay_for_clocks(m, ui, clks):
		clks -= 1 # because one cycle is used in setting up this timer
		clks += self.clks_adjust # the clks_adjust is so pipeline delays can be accounted for if needed
		try:
			assert clks > 0, "unable to implement a delay of 0 in this way"
		except TypeError:
			pass

		done = Signal()
		with m.FSM(name="set_timer_clks_fsm") as fsm:
			m.d.comb += done.eq(fsm.ongoing("DONE"))
			
			with m.State("IDLE"):
				# assert that it is actually idle?
				# or otherwise, wait for it to be idle
				with m.If(~ui.active):
					m.next = "LOAD"
			
			with m.State("LOAD"):
				m.d.sync += [
					ui.load_in.eq(clks),
					ui.start.eq(1)
				]
				m.next = "LOADED"
			
			with m.State("LOADED"):
				m.d.sync += ui.start.eq(0),
				m.next = "WAIT"
			
			with m.State("WAIT"):
				with m.If(ui.done):
					m.next = "DONE"

			with m.State("DONE"):
				m.next = "IDLE"

		return done
		

	def elaborate(self, platform = None):
		m = Module()

		ui = Record.like(self.ui)
		debug = Record.like(self.debug)
		m.d.sync += [
			self.ui.connect(ui),
			self.debug.connect(debug)
		]

		m.submodules.delayer = delayer = Timer(load=int(self.load))

		m.d.sync += [
			delayer.start.eq(ui.trigger), # comb?
			ui.done.eq(delayer.done),
			debug.count.eq(delayer.counter_out),
			ui.active.eq(delayer.counter_out != self.load)
		]

		return m


# sys.path.append(os.path.join(os.getcwd(), "tests/ulx3s_gui_test/common"))
# from test_common import fpga_gui_interface, fpga_mcu_interface
# addrs = fpga_mcu_interface.register_addresses

class timerTest(Elaboratable):
	ui_layout = [
		("trigger",	1,	DIR_FANOUT),
		("done",	1,	DIR_FANIN)
	]

	debug_layout = [
		("count",	32,	DIR_FANIN)
	]

	def __init__(self, load):
		super().__init__()
		self.ui = Record(timerTest.ui_layout)
		self.debug = Record(timerTest.debug_layout)
		self.load = load

	def elaborate(self, platform: Platform) -> Module:
		m = Module()

		ui = Record.like(self.ui)
		debug = Record.like(self.debug)
		m.d.sync += [
			self.ui.connect(ui),
			self.debug.connect(debug)
		]

		m.submodules.delayer = delayer = Timer(load=int(self.load))

		m.d.sync += [
			delayer.start.eq(ui.trigger), # comb?
			ui.done.eq(delayer.done),
			debug.count.eq(delayer.counter_out)
		]

		return m

if __name__ == "__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	class Testbench(Elaboratable):
		timerTest_test_interface_layout = [
			("trigger",			1, DIR_FANOUT),
			("done",			1, DIR_FANIN),
			("reset",			1, DIR_FANOUT), # note - this doesn't seem to show in traces, but still works?
			# ("leds", 			8, DIR_FANOUT) # can't do reset-less here, so using a separate signal
		]

		
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
			# for i, each in enumerate([ui.trigger, ui.done, ui.reset]):
			# 	with m.If(Rose(each)):
			# 		m.d.sync += self.leds[i].eq(~self.leds[i])
			m.d.sync_1e6 += self.leds.eq(debug.count[10:])

			def init_clocks():
				### add default clock
				m.domains.sync = cd_sync = ClockDomain("sync")
				m.d.sync += cd_sync.rst.eq(ui.reset) # or should this be comb?
				if platform != None:
					m.d.comb += cd_sync.clk.eq(platform.request("clk25"))
					platform.add_clock_constraint(cd_sync.clk,  platform.default_clk_frequency)
				else:
					... # note - the sim clock is added later

				### add slower clock for counters (i.e. so they don't limit speed)
				m.domains.sync_1e6 = cd_sync_1e6 = ClockDomain("sync_1e6")
				divisor = 25
				clk_counter = Signal(shape=range(int(divisor/2)+1)) # is this right?
				m.d.sync += [
					clk_counter.eq(Mux(clk_counter == (int(divisor/2)-1), 0, clk_counter+1)), # not quite accurate but close enough
					cd_sync_1e6.rst.eq(ui.reset), # or should this be comb?
					cd_sync_1e6.clk.eq(Mux(clk_counter==0,~cd_sync_1e6.clk,cd_sync_1e6.clk))
				]
			init_clocks()

			return m

	if args.action == "generate":
		pass

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

					yield from strobe(self.ui.trigger)

					while not (yield self.ui.done):
						yield

					# yield Delay(100e-6)

					yield Delay(1e-6) # delay at end

					# now do a reset
					
					yield from strobe(self.ui.reset)
					# yield from strobe(ClockSignal().rst)


			def elaborate(self, platform = None):
				m = Module()

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
		...
		from amtest.boards.ulx3s.common import platform, UploadBase

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

