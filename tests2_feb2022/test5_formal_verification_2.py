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


class RefreshTimer(Elaboratable):
	"""Refresh Timer

	Generate periodic pulses (tREFI period) to trigger DRAM refresh.
	"""

	def __init__(self, trefi, utest: FHDLTestCase = None):
		if trefi < 2:
			raise ValueError("trefi values under 2 are currently unsupported")

		self.wait = Signal()
		self.done = Signal()
		self.count = Signal(range(trefi), reset=trefi-1)
		self._trefi = trefi
		self.utest = utest

	def elaborate(self, platform):
		m = Module()

		trefi = self._trefi

		with m.If(self.wait & (self.count != 0)):
			m.d.sync += self.count.eq(self.count-1)

			with m.If(self.count == 1):
				m.d.sync += self.done.eq(1)
		with m.Else():
			m.d.sync += [
				self.count.eq(self.count.reset),
				self.done.eq(0),
			]

		if platform == "formal":
			test_id = self.utest.get_test_id()
			if test_id == "RefreshTimerTestCase":
				m.d.comb += Assert(self.done == (self.count == 0))
			
			elif test_id == "RefreshTimerTestCase2":
				m.d.comb += Cover(self.done == 1)

			elif test_id == "RefreshTimerTestCase3":
				with m.If(~Initial()):
					m.d.sync += Assert(self.done == 5)

			else:
				assert 0, f"Invalid test requested: {self.test_id}"

		return m




if __name__=="__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	if args.action == "generate":
		class RefreshTimerTestCase(FHDLTestCase):
			def test_formal(self):
				def generic_test(tREFI):
					dut = RefreshTimer(tREFI, utest=self)
					self.assertFormal(dut, mode="bmc", depth=tREFI+1)
				[generic_test(_) for _ in [2, 5, 10]]

		class RefreshTimerTestCase2(FHDLTestCase):
			def test_formal(self):
				tREFI = 5
				dut = RefreshTimer(tREFI, utest=self)
				self.assertFormal(dut, mode="cover", depth=tREFI+1)

		class RefreshTimerTestCase3(FHDLTestCase):
			def test_formal(self):
				tREFI = 5
				dut = RefreshTimer(tREFI, utest=self)
				self.assertFormal(dut, mode="hybrid", depth=tREFI+1)

		import unittest
		sys.argv[1:] = [] # so the args used for this file don't interfere with unittest
		unittest.main()
	
	else:
		assert 0, "Not implemented"


