import sys, os
from termcolor import cprint
from typing import List
import textwrap

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


from amlib.io import SPIRegisterInterface, SPIDeviceBus, SPIMultiplexer
from amlib.debug.ila import SyncSerialILA
# from amlib.utils.cdc import synchronize
from amlib.utils import Timer

from amtest.boards.ulx3s.common.upload import platform, UploadBase
from amtest.boards.ulx3s.common.clks import add_clock
from amtest.utils import FHDLTestCase


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
		self.load = int(load)
		self.utest = utest

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

		# note that if self.utest is none, then another class (not this one) is being tested, so skip this
		if (platform == "formal") & (self.utest != None):
			test_id = self.utest.get_test_id()
			if test_id == "tryToTest_timerTest":
				m.d.sync += Assert(ui.done != (debug.count == 0))

		return m


if __name__=="__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	class Testbench(Elaboratable):
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
		class tryToTest_timerTest(FHDLTestCase):
			def test_formal(self):
				def generic_test(load):
					dut = timerTest(load, utest=self)
					self.assertFormal(dut, mode="bmc", depth=load+1)
				[generic_test(load) for load in [2, 5, 10]]

		class tryToTest_Testbench(FHDLTestCase):
			def test_formal(self):
				dut = Testbench(utest=self)
				self.assertFormal(dut, mode="cover", depth=200)

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



