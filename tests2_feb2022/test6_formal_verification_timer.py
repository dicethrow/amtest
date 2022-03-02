import sys, os
from termcolor import cprint
from typing import List
import textwrap
import numpy as np
import enum

from amaranth import Elaboratable, Module, Signal, Mux, ClockSignal, ClockDomain, ResetSignal, Cat, Const
from amaranth.hdl.ast import Rose, Stable, Fell, Past, Initial
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
from amaranth.utils import bits_for

from amaranth_boards.ulx3s import ULX3S_85F_Platform

from amlib.io import SPIRegisterInterface, SPIDeviceBus, SPIMultiplexer
from amlib.debug.ila import SyncSerialILA
# from amlib.utils.cdc import synchronize
from amlib.utils import Timer

from amtest.boards.ulx3s.common.upload import platform, UploadBase
from amtest.boards.ulx3s.common.clks import add_clock
from amtest.utils import FHDLTestCase


class Delayer(Elaboratable):
	""" 
	Desired usage: 
		...
		with m.If(delayer1.delay_for_time(m, 4e-6))
			m.next = "REQUEST_REFRESH_SOON"
		...

	Ideas:
		- What clock should this be fed? A slower clock?
		- How to handle short periods? Past(xxx, y)?

		- ok let's just stick with the sync clock here for now	

	"""
	ui_layout = [
		# ("start",		1,	DIR_FANOUT),
		("done",		1,	DIR_FANIN),
		("inactive",	1,	DIR_FANIN)
		# ("load",	) # note - added in __init__
		# ("active",	1,	DIR_FANIN)
	]

	debug_layout = [
		# ("count",	32,	DIR_FANIN)
	]

	def __init__(self, clk_freq, utest: FHDLTestCase = None):
		super().__init__()
		self.utest = utest
		self.clk_freq = clk_freq

		if "load" not in [field for field, _, _ in Delayer.ui_layout]:
			Delayer.ui_layout.append(("load", self._get_counter_bitwidth(), DIR_FANOUT))

		self.ui = Record(Delayer.ui_layout)
		# self.debug = Record(Delayer.debug_layout)


	def _get_counter_bitwidth(self):
		longest_period = 1.1 * 100e-6 # is this an OK assumption?
		return bits_for(int(np.ceil(longest_period * self.clk_freq)))
	
	def delay_for_time(self, m, duration_sec):
		if isinstance(duration_sec, enum.Enum):
			duration_sec = duration_sec.value

		clks = int(np.ceil(duration_sec * self.clk_freq))
		return self.delay_for_clks(m, clks)
		...
	
	def delay_for_clks(self, m, clks):
		# note: This is designed as an interface, to be used by other modules.
		# This means that .sync here will probably not 
		# recognise the use of DomainRenamer() if used.
		# That's why self.domain is passed as an init argument, so we can access it like this:

		print("Clks is ", clks)
		assert clks > 0, "Not enough clocks to delay in this way. todo: correct threshold"
		
		with m.FSM(name="delay_fsm"):#, domain=self.domain):
			with m.State("INIT"):
				m.d.sync += self.ui.load.eq(clks)
				m.next = "LOADED"
			with m.State("LOADED"):
				m.d.sync += self.ui.load.eq(0)
				m.next = "DONE"
			with m.State("DONE"): # is this extra state needed? to avoid driving ui.load?
				...

		return self.ui.done

	def elaborate(self, platform):
		m = Module()

		_ui = Record.like(self.ui)
		# _debug = Record.like(self.debug)
		m.d.sync += [
			self.ui.connect(_ui),
			# self.debug.connect(_debug)
		]

		countdown = Signal(shape=self._get_counter_bitwidth())

		def add_countdown_behaviour():
			m.d.sync += [
				countdown.eq(Mux(countdown>0, countdown-1, countdown)),
				_ui.done.eq(countdown==1), # so a single pulse will occur as it reaches 0
				_ui.inactive.eq( (countdown==0) & ~_ui.done )
			]
		
		def add_reload_behaviour():
			with m.If(_ui.load != 0):
				m.d.sync += countdown.eq(_ui.load) # and plus one? or +/- a bias?
		
		add_countdown_behaviour()
		add_reload_behaviour()

		return m


class timerTest(Elaboratable):
	ui_layout = [
		("start",	1,	DIR_FANOUT),
		("done",	1,	DIR_FANIN),
		("active",	1,	DIR_FANIN)
	]

	debug_layout = [
		("count",	32,	DIR_FANIN)
	]

	def __init__(self, load, utest: FHDLTestCase = None):
		super().__init__()
		self.ui = Record(timerTest.ui_layout)
		self.debug = Record(timerTest.debug_layout)
		self.load = int(load - 5)
		self.utest = utest

	def elaborate(self, platform: Platform) -> Module:
		m = Module()

		_ui = Record.like(self.ui)
		_debug = Record.like(self.debug)
		m.d.sync += [
			self.ui.connect(_ui),
			self.debug.connect(_debug)
		]

		m.submodules.delayer = delayer = Timer(load=self.load)

		m.d.sync += [
			delayer.start.eq(_ui.start),
			_ui.done.eq(delayer.done),
			_debug.count.eq(delayer.counter_out),
			# _ui.active.eq(delayer.counter_out != self.load)
		]

		with m.If(Rose(_ui.start)):
			m.d.sync += _ui.active.eq(1)
		with m.Elif(Fell(_ui.done)):
			m.d.sync += _ui.active.eq(0)

		# note that if self.utest is none, then another class (not this one) is being tested, so skip this
		if (platform == "formal") & (self.utest != None):
			test_id = self.utest.get_test_id()
			if test_id == "tryToTest_timerTest":
				m.d.sync += Assert(_ui.done != (_debug.count == 0))

		return m


if __name__=="__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	class Testbench(Elaboratable):
		Testbench_ui_layout = [
			("tb_done", 	1,	DIR_FANIN),
		] + Delayer.ui_layout # todo - how to make the sharedTimer.ui layout be nested?

		def __init__(self, utest: FHDLTestCase = None):
			super().__init__()
			self.ui = Record(Testbench.Testbench_ui_layout)
			# self.leds = Signal(8, reset_less=True)
			self.utest = utest

		def elaborate(self, platform = None):
			m = Module()

			# m.submodules.delayer = delayer = DomainRenamer("sync_1e6")(Delayer(clk_freq=1e6, domain="sync_1e6"))
			m.submodules.delayer = delayer = Delayer(clk_freq=24e6)

			_ui = Record(Testbench.Testbench_ui_layout) #.like(self.ui)
			# m.d.sync_1e6 += [
			m.d.sync += [
				self.ui.connect(_ui),
				_ui.connect(delayer.ui, exclude=["tb_done"])
			]
				

			if isinstance(self.utest, FHDLTestCase):
				assert platform == None, f"Unexpected platform status of {platform}"
				# assert platform == "formal", "This test can only run in formal mode"
				add_clock(m, "sync")
				# add_clock(m, "sync_1e6")
				test_id = self.utest.get_test_id()
				if test_id == "RefreshTimerTestCase":
					with m.FSM(name="testbench_fsm", domain="sync") as fsm:
						m.d.sync += _ui.tb_done.eq(fsm.ongoing("DONE"))

						with m.State("INITIAL"):
							m.next = "START"

						with m.State("START"):
							with m.If(delayer.delay_for_time(m, 2e-6)):
								m.next = "START2"

						with m.State("START2"):
							with m.If(delayer.delay_for_time(m, 3e-6)):
								m.next = "DONE"
						
						with m.State("DONE"):
							...

			elif isinstance(platform, ULX3S_85F_Platform): 
				# then this is the test that is run when uploaded
				...

			return m


	class Testbench2(Elaboratable):
		timerTest_test_interface_layout = [
			# ("reset",			1, DIR_FANOUT), # note - this doesn't seem to show in traces, but still works?
			# ("leds", 			8, DIR_FANOUT) # can't do reset-less here, so using a separate signal
		] + timerTest.ui_layout

		
		def __init__(self, utest: FHDLTestCase = None):
			super().__init__()
			self.ui = Record(Testbench.timerTest_test_interface_layout)
			self.leds = Signal(8, reset_less=True)
			self.utest = utest

		def elaborate(self, platform = None):
			m = Module()

			m.submodules.dut = dut = DomainRenamer("sync_1e6")(timerTest(load = 1e2))# if platform == None else 1e6))

			ui = Record.like(self.ui)
			debug = Record.like(dut.debug)
			m.d.sync_1e6 += [
				self.ui.connect(ui),
				ui.connect(dut.ui),
				debug.connect(dut.debug)
			]

			# change a led flag each time one of these rises, so we can see quick changes
			# for i, each in enumerate([ui.start, ui.done, ui.reset, ui.active]):
			# 	with m.If(Rose(each)):
			# 		m.d.sync += self.leds[i].eq(~self.leds[i])
			m.d.sync_1e6 += self.leds.eq(debug.count[15:])

			if (platform == "formal") & (self.utest != None):
				test_id = self.utest.get_test_id()
				if test_id == "tryToTest_Testbench":
					m.d.comb += Cover(ui.done)

			return m

	if args.action == "generate":

		class testDesiredInterface_withExpectedBehaviour(FHDLTestCase):
			def test_sim(self): # note, it's only formal if assertFormal() is used
				def test(load):
					dut = Testbench(utest=self)
					
					def process():
						# elapsed_clks = 0

						for _ in range(200):
							if not (yield dut.ui.tb_done):
								yield

						# while not (yield dut.ui.tb_done):
						# 	yield
						# yield dut.ui.start.eq(1); 
						# yield; elapsed_clks += 1
						# yield dut.ui.start.eq(0)
						# while not (yield dut.ui.done):
						# 	yield; elapsed_clks += 1
						
						# print(f"Elapsed clks: {elapsed_clks}, load: {load}, elapsed_clks-load={elapsed_clks-load}")
						
						# for x in range(2*load): # arbitary
						# 	yield
						
					
					sim = Simulator(dut)
					sim.add_clock(1/25e6, domain="sync")
					sim.add_sync_process(process)

					with sim.write_vcd(
						f"{current_filename}_{self.get_test_id()}_load={load}.vcd"):
						sim.run()

				[test(load) for load in range(10, 15) ]

		# class tryToTest_timerTest(FHDLTestCase):
		# 	def test_formal(self):
		# 		def generic_test(load):
		# 			dut = timerTest(load, utest=self)
		# 			self.assertFormal(dut, mode="bmc", depth=load+1)
		# 		[generic_test(load) for load in [2, 5, 10]]

		# class tryToTest_Testbench(FHDLTestCase):
		# 	def test_formal(self):
		# 		dut = Testbench(utest=self)
		# 		self.assertFormal(dut, mode="cover", depth=200) # why 200? arbitary?

		# class RefreshTimerTestCase3(FHDLTestCase):
		# 	def test_formal(self):
		# 		tREFI = 5
		# 		dut = RefreshTimer(tREFI, utest=self)
		# 		self.assertFormal(dut, mode="hybrid", depth=tREFI+1)

		import unittest
		sys.argv[1:] = [] # so the args used for this file don't interfere with unittest
		unittest.main()
	
	elif args.action == "simulate":
		class Simulate(Testbench):
			def __init__(self):
				super().__init__()
				self.reset_sync_1e6 = Signal(reset_less=True)

			def elaborate(self, platform = None):
				m = super().elaborate(platform)

				# add slower clock for counters (i.e. so they don't limit speed)					
				add_clock(m, "sync_1e6")
				add_clock(m, "sync")

				# note that this workaround is needed because the simulation
				# can't work with ResetSignal() directly for some reason
				m.d.sync_1e6 += ResetSignal("sync_1e6").eq(self.reset_sync_1e6)
				
				return m
			
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

					if True: # often this block will hang if the design is broken
						while not (yield self.ui.done):
							yield
					else: # in that case, use this instead
						yield Delay(100e-6)

					yield Delay(1e-6) # delay at end

					# now do a reset
					yield from strobe(self.reset_sync_1e6)
				
				yield self.reset_sync_1e6.eq(1)
				yield Delay(100e-6)

		top = Simulate()
		sim = Simulator(top)
		sim.add_clock(1/25e6, domain="sync")
		sim.add_sync_process(top.timer_test, domain="sync_1e6")

		with sim.write_vcd(
			f"{current_filename}_simulate.vcd",
			f"{current_filename}_simulate.gtkw"):

			sim.run()

	else: # then upload
		class Upload(UploadBase):
			def __init__(self):
				super().__init__()
				
			def elaborate(self, platform = None):
				m = super().elaborate(platform)

				m.submodules.tb = tb = Testbench()	

				ui = Record.like(tb.ui)
				m.d.sync_1e6 += ui.connect(tb.ui)

				start = Signal.like(ui.start)

				# don't manually route the reset - do this, 
				# otherwise, if Records are used, they will oscillate, as can't be reset_less
				m.d.sync_1e6 += ResetSignal("sync_1e6").eq(self.i_buttons.right) 

				# reset = Signal.like(ui.reset, reset_less=True) 
				m.d.sync_1e6 += [
					start.eq(self.i_buttons.left),
					ui.start.eq(Rose(start, domain="sync_1e6")),
					self.leds.eq(tb.leds),
				]

				return m
		
		platform.build(Upload(), do_program=False, build_dir=f"{current_filename}_build")



