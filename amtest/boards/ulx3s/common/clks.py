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
from amaranth.build import Platform


from amlib.io import SPIRegisterInterface, SPIDeviceBus, SPIMultiplexer
from amlib.debug.ila import SyncSerialILA
# from amlib.utils.cdc import synchronize
from amlib.utils import Timer
from amaranth.lib.cdc import FFSynchronizer

def add_clock(m, name, *, reset = None, platform = None):
	if name == "sync_1e6":
		### add slower clock for counters (i.e. so they don't limit speed)
		m.domains.sync_1e6 = cd_sync_1e6 = ClockDomain("sync_1e6")
		divisor = 25
		clk_counter = Signal(shape=range(int(divisor/2)+1)) # is this right?
		m.d.sync += [
			clk_counter.eq(Mux(clk_counter == (int(divisor/2)-1), 0, clk_counter+1)), # not quite accurate but close enough
			cd_sync_1e6.clk.eq(Mux(clk_counter==0,~cd_sync_1e6.clk,cd_sync_1e6.clk))
		]

		if isinstance(reset, Signal):
			m.d.sync += cd_sync_1e6.rst.eq(reset) # or should this be comb?
	
	elif name == "sync":
		m.domains.sync = cd_sync = ClockDomain("sync")

		if isinstance(platform, Platform):
			m.d.comb += cd_sync.clk.eq(platform.request("clk25"))
			platform.add_clock_constraint(cd_sync.clk,  platform.default_clk_frequency)
		else:
			... # in this case, assume that this clock is added manually to the simulator
			# Could the simulator instead be passed and dealt with here?
		


	else:
		assert 0, f"clock {name} not implemented"

