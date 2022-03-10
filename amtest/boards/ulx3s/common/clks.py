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

from .ECP5PLL import ECP5PLL

# sync_made_yet = False

def add_clock(m, name, *, reset = None, platform = None):
	if name == "sync_1e6":
		### add slower clock for counters (i.e. so they don't limit speed)
		m.domains.sync_1e6 = cd_sync_1e6 = ClockDomain("sync_1e6")
		divisor = 25
		 # resetless, so resetting sync domain won't break sync_1e6?
		 # actually that doesn't work somehow. Instead - don't reset sync.
		clk_counter = Signal(shape=range(int(divisor/2)+1))#, reset_less=True)
		m.d.sync += [
			clk_counter.eq(Mux(clk_counter == (int(divisor/2)-1), 0, clk_counter+1)), # not quite accurate but close enough
			cd_sync_1e6.clk.eq(Mux(clk_counter==0,~cd_sync_1e6.clk,cd_sync_1e6.clk))
		]

		if isinstance(reset, Signal):
			m.d.sync += cd_sync_1e6.rst.eq(reset) # or should this be comb?
	
	elif name == "sync_and_143e6_sdram_from_pll":
		# assert sync_made_yet == False, "sync clock already made, cannot remake. Check order of calls to this function"

		sdram_freq = 143e6

		# based on examples/blackicemx_nmigen_examples/retro/retro_test.py by emard
		clk_in = platform.request(platform.default_clk, dir='-')[0]

		# Clock generator.
		m.domains.sync  = cd_sync  = ClockDomain("sync")
		m.domains.sdram = cd_sdram = ClockDomain("sdram")

		m.submodules.ecp5pll = pll = ECP5PLL()
		pll.register_clkin(clk_in,  platform.default_clk_frequency)
		pll.create_clkout(cd_sync,  platform.default_clk_frequency)
		pll.create_clkout(cd_sdram, sdram_freq)

		platform.add_clock_constraint(cd_sync.clk,  platform.default_clk_frequency)
		platform.add_clock_constraint(cd_sdram.clk, sdram_freq)

		# sync_made_yet = True
	
	elif name == "sync":
		# assert sync_made_yet == False, "sync clock already made, cannot remake. Check order of calls to this function"
		
		m.domains.sync = cd_sync = ClockDomain("sync")

		if isinstance(platform, Platform):
			m.d.comb += cd_sync.clk.eq(platform.request("clk25"))
			platform.add_clock_constraint(cd_sync.clk,  platform.default_clk_frequency)
		else:
			... # in this case, assume that this clock is added manually to the simulator
			# Could the simulator instead be passed and dealt with here?
		
		# sync_made_yet = True


	else:
		assert 0, f"clock {name} not implemented"

