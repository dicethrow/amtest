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

	Performance:
		- speed
			- From the top.tim file after running 'build' for upload:
			Info: Max frequency for clock '$glbnet$clk': 212.09 MHz (PASS at 25.00 MHz)
			- I think this is fine 

		- delay
			- can implement delays down to 2 clock cycles - which is great! woo-hoo!
			- this is by having two separate timer mechanisms: one for large delays,
			and one for small delays (less than 8 or so clock cycles)

	"""

	ui_layout = [
		("done",		1,	DIR_FANIN),
		("inactive",	1,	DIR_FANIN),
		("load",		12, DIR_FANOUT) # should be dynamic but doesn't work. Assume it's 12bits wide
	]

	debug_layout = [
		# ("count",	32,	DIR_FANIN)
	]

	def __init__(self, clk_freq, utest: FHDLTestCase = None):
		super().__init__()
		self.utest = utest
		self.clk_freq = clk_freq
		self.longest_period = 1.1 * 100e-6 # is this an OK assumption?

		assert self._get_counter_bitwidth() == 12, f"Not sure how to make this dynamic, so update this if it fails. It is: {self._get_counter_bitwidth()}"
		# if "load" not in [field for field, _, _ in Delayer.ui_layout]:
		# 	Delayer.ui_layout.append(("load", self._get_counter_bitwidth(), DIR_FANOUT))

		self.ui = Record(Delayer.ui_layout)
		# self.debug = Record(Delayer.debug_layout)


	def _get_counter_bitwidth(self):
		return bits_for(int(np.ceil(self.longest_period * self.clk_freq)))
	
	def delay_for_time(self, m, _ui, duration_sec):
		if isinstance(duration_sec, enum.Enum):
			duration_sec = duration_sec.value

		clks = int(np.ceil(duration_sec * self.clk_freq))

		return self.delay_for_clks(m, _ui, clks)
	
	def delay_for_clks(self, m, _ui, clks):
		# note: This is designed as an interface, to be used by other modules.
		# This means that .sync here will probably not 
		# recognise the use of DomainRenamer() if used.
		# That's why self.domain is passed as an init argument, so we can access it like this:
		print("Clks is ", clks)

		if clks > 8:
			clks -= 8 # this compensates for delays etc in the implementation
			assert self._get_counter_bitwidth() >= bits_for(clks), f"""The desired delay of {clks} clks 
				requires {bits_for(clks)} bits, but this timer assumes {self.longest_period}
				sec with {self._get_counter_bitwidth()} as the max"""
			# assert clks > 0, "Not enough clocks to delay in this way. todo: correct threshold"
			
			with m.FSM(name="delay_fsm"):#, domain=self.domain):
				with m.State("INIT"):
					m.d.sync += _ui.load.eq(clks)
					m.next = "LOADED"
				with m.State("LOADED"):
					m.d.sync += _ui.load.eq(0)
					m.next = "DONE"
				with m.State("DONE"): # is this extra state needed? to avoid driving ui.load?
					...

			return _ui.done
		
		elif (clks <= 8) and (clks > 1): # "this technique may not work efficiently for larger clks"
			print("Using smaller shifter")
			clks -= 1
			shift_timer = Signal(reset=-1, shape=clks)
			m.d.sync += shift_timer.eq(shift_timer[1:])
			return shift_timer == 1
		
		elif clks == 1:
			return True

		else:
			assert 0, f"Unable to implement a timer for clocks of {clks}"


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
				_ui.inactive.eq( (countdown==0) )#& ~_ui.done )
			]
		
		def add_reload_behaviour():
			with m.If(_ui.load != 0):
				m.d.sync += countdown.eq(_ui.load) # and plus one? or +/- a bias?
		
		add_countdown_behaviour()
		add_reload_behaviour()

		return m


if __name__=="__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	class Testbench(Elaboratable):
		Testbench_ui_layout = [
			("tb_fanin_flags", 	[
				("in_start",	1,	DIR_FANIN),
				("in_done",		1,	DIR_FANIN),
			]),
			("tb_fanout_flags",[
				("trigger",		1,	DIR_FANOUT)
			])
		] + Delayer.ui_layout # todo - how to make the sharedTimer.ui layout be nested?

		def __init__(self, clk_freq = 24e6, utest: FHDLTestCase = None):
			super().__init__()
			self.ui = Record(Testbench.Testbench_ui_layout)
			self.clk_freq = clk_freq
			self.utest = utest

		def elaborate(self, platform = None):
			m = Module()

			m.submodules.delayer = delayer = Delayer(clk_freq=self.clk_freq)

			_ui = Record(Testbench.Testbench_ui_layout) #.like(self.ui)
			# m.d.sync_1e6 += [
			m.d.sync += [
				self.ui.connect(_ui),
				_ui.connect(delayer.ui, exclude=["tb_fanin_flags", "tb_fanout_flags"])
			]
				

			if isinstance(self.utest, FHDLTestCase):
				add_clock(m, "sync")
				# add_clock(m, "sync_1e6")
				test_id = self.utest.get_test_id()

				# note that this workaround is needed because the simulation
				# can't work with ResetSignal() directly for some reason
				# reset_sync = Signal(reset_less=True)
				# m.d.sync += ResetSignal("sync").eq(reset_sync)

				if test_id == "testDesiredInterface_withExpectedBehaviour":
					assert platform == None, f"Unexpected platform status of {platform}"

					with m.FSM(name="testbench_fsm") as fsm:
						# m.d.sync += _ui.tb_done.eq(fsm.ongoing("DONE"))
						m.d.sync += [
							_ui.tb_fanin_flags.in_start.eq(fsm.ongoing("START")),
							_ui.tb_fanin_flags.in_done.eq(fsm.ongoing("DONE"))
						]

						with m.State("INITIAL"):
							m.next = "START"

						with m.State("START"):
							with m.If(delayer.delay_for_time(m, _ui, self.utest.test_period)):
								m.next = "DONE"
						
						with m.State("DONE"):
							...

				elif test_id == "formalTests_thatDelayWorks":
					assert platform == "formal", "This test can only run in formal mode"

					timer_done = Signal()
					timer_ought_to_finish = Signal()

					m.d.comb += [
						timer_done.eq(delayer.delay_for_time(m, _ui, self.utest.test_period)),
						timer_ought_to_finish.eq(Past(Initial(), clocks=self.utest.expected_clks)),
					]

					# agh! how to handle reset properly?

					# when not in reset
					with m.If(~ResetSignal("sync")):
						# Only permit load to be used when inactive
						m.d.sync += Assume(delayer.ui.inactive.implies(delayer.ui.load == 0)) # although this won't work with the fast clock..?

						m.d.sync += Assert(timer_done == timer_ought_to_finish)



			elif isinstance(platform, ULX3S_85F_Platform): 
				print("Doing the upload part now")
				# then this is the test that is run when uploaded
				with m.FSM() as fsm:

					m.d.sync += [
						_ui.tb_fanin_flags.in_start.eq(fsm.ongoing("START")),
						_ui.tb_fanin_flags.in_done.eq(fsm.ongoing("DONE"))
					]

					with m.State("INITIAL"):
						with m.If(_ui.tb_fanout_flags.trigger):
							m.next = "START"
					
					with m.State("START"):
						with m.If(delayer.delay_for_time(m, _ui, 100e-6)): # although still too short to see
							m.next = "DONE"
					
					with m.State("DONE"):
						... # hang here until reset?


			return m


	if args.action == "generate": # formal testing

		class formalTests_thatDelayWorks(FHDLTestCase):
			def test_formal(self):
				def test(period):
					self.test_period = period
					self.clk_freq = 24e6

					def min_num_of_clk_cycles(freq_hz, period_sec):
						return int(np.ceil(period_sec * freq_hz))

					self.expected_clks = min_num_of_clk_cycles(self.clk_freq, self.test_period)
					dut = Testbench(clk_freq=self.clk_freq, utest=self)
					self.assertFormal(dut, mode="bmc", depth=self.expected_clks*2) # or cover/hybrid?
				[test(period) for period in [1e-6, 100e-9, 50e-9, 10e-9, 1e-9] ]

		...
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

	
	elif args.action == "simulate":
		
		class testDesiredInterface_withExpectedBehaviour(FHDLTestCase):
			def test_sim(self):
				def test(period):
					self.test_period = period
					self.clk_freq = 24e6
					dut = Testbench(clk_freq=self.clk_freq, utest=self)

					def min_num_of_clk_cycles(freq_hz, period_sec):
						return int(np.ceil(period_sec * freq_hz))

					expected_clks = min_num_of_clk_cycles(self.clk_freq, self.test_period)
					
					def process():
						# elapsed_clks = 0

						started = False
						measured_clks = 0
						test_clks = 0
					
						while True:
							if (yield dut.ui.tb_fanin_flags.in_start) or started:
								started = True
								measured_clks += 1
							
							if (yield dut.ui.tb_fanin_flags.in_done):
								break
							
							test_clks += 1
							if test_clks > (2*expected_clks) + 50:
								print("Timeout, aborting")
								break

							yield
						
						

						
						print( f"The timer took with {measured_clks} cycles, but should have taken {expected_clks}")
						# self.assertEqual(expected_clks, measured_clks, f"The timer took with {measured_clks} cycles, but should have taken {expected_clks}")
					
					sim = Simulator(dut)
					sim.add_clock(period=1/self.clk_freq, domain="sync")
					sim.add_sync_process(process)

					with sim.write_vcd(
						f"{current_filename}_{self.get_test_id()}_period={period}.vcd"):
						sim.run()

				[test(period) for period in [100e-6, 10e-6, 1e-6, 100e-9, 50e-9, 10e-9, 1e-9] ]

	if args.action in ["generate", "simulate"]:
		# now run each FHDLTestCase above 
		import unittest
		sys.argv[1:] = [] # so the args used for this file don't interfere with unittest
		unittest.main()

	else: # otherwise, upload
		class Upload(UploadBase):
			def __init__(self):
				super().__init__()
				
			def elaborate(self, platform = None):
				m = super().elaborate(platform)

				m.submodules.tb = tb = Testbench()	

				ui = Record.like(tb.ui)
				m.d.sync += ui.connect(tb.ui)

				def start_on_left_button():
					start = Signal.like(self.i_buttons.left)
					m.d.sync += [
						start.eq(self.i_buttons.left),
						ui.tb_fanout_flags.trigger.eq(Rose(start))
					]

				def reset_on_right_button():
					# don't manually route the reset - do this, 
					# otherwise, if Records are used, they will oscillate, as can't be reset_less
					m.d.sync += ResetSignal("sync").eq(self.i_buttons.right) 

				def display_on_leds():
					m.d.comb += self.leds.eq(Cat([
						ui.tb_fanin_flags.in_start,	# this should very briefly flash on after pressing start
						ui.tb_fanin_flags.in_done,	# this should stay on when pressing start, and off after reset
						self.i_buttons.right,  		# led indicates that the start button was pressed
						self.i_buttons.left			# led indicates that the reset button was pressed
					]))

				start_on_left_button()
				reset_on_right_button()
				display_on_leds()

				return m
		
		platform.build(Upload(), do_program=False, build_dir=f"{current_filename}_build")



