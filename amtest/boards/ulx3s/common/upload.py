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

from amlib.io import SPIRegisterInterface, SPIDeviceBus, SPIMultiplexer
from amlib.debug.ila import SyncSerialILA
# from amlib.utils.cdc import synchronize
from amlib.utils import Timer
from amaranth.lib.cdc import FFSynchronizer
from amaranth.build import Platform

from amaranth.build import Platform, Resource, Subsignal, Pins, PinsN, Attrs
from amaranth_boards.ulx3s import ULX3S_85F_Platform

from .clks import add_clock
from ....utils import Params

# ESP-32 connections
esp32_spi = [
	Resource("esp32_spi", 0,
		Subsignal("en",     Pins("F1", dir="o"), Attrs(PULLMODE="UP")),
		Subsignal("tx",     Pins("K3", dir="o"), Attrs(PULLMODE="UP")),
		Subsignal("rx",     Pins("K4", dir="i"), Attrs(PULLMODE="UP")),
		Subsignal("gpio0",  Pins("L2"),          Attrs(PULLMODE="UP")),
		Subsignal("gpio4_copi", Pins("H1", dir="i"),  Attrs(PULLMODE="UP")), # SDD1? GPIO4? 
		Subsignal("gpio5_cs",  PinsN("N4", dir="i"),  Attrs(PULLMODE="UP")),
		Subsignal("gpio12_cipo", Pins("K1", dir="o"),  Attrs(PULLMODE="UP")), # SDD2? GPIO12?
		Subsignal("gpio16_sclk", Pins("L1", dir="i"),  Attrs(PULLMODE="UP")),
		Attrs(IO_TYPE="LVCMOS33", DRIVE="4")
	),
]

# digital discovery connection, for logic probing
digital_discovery = [
	Resource("digital_discovery", 0,
		Subsignal("bus", Pins("14- 14+ 15- 15+ 16- 16+ 17- 17+ 18- 18+", dir="o", conn=("gpio", 0)), Attrs(IO_TYPE="LVCMOS25"))
	)
]

platform = ULX3S_85F_Platform()
platform.add_resources(esp32_spi)
platform.add_resources(digital_discovery)


class UploadBase(Elaboratable):
	def __init__(self):
		super().__init__()
		self.config_params = Params()
		self.test_params = Params()

	def elaborate(self, platform = None):
		self.leds = Cat([platform.request("led", i) for i in range(8)])
		self.esp32 = platform.request("esp32_spi")
		io_uart = platform.request("uart")
		# clk25 = platform.request("clk25")

		i_unsync_buttons = Record([
			("pwr",			1, DIR_FANOUT),
			("fireA",		1, DIR_FANOUT),
			("fireB",		1, DIR_FANOUT),
			("up",			1, DIR_FANOUT),
			("down",		1, DIR_FANOUT),
			("left",		1, DIR_FANOUT),
			("right",		1, DIR_FANOUT),
		])

		m = Module()

		if hasattr(self.config_params, "sync_mode"):
			add_clock(m, self.config_params.sync_mode, platform=platform) # for pll capability 		# add_clock(m, "sync", platform=platform)
		else:
			add_clock(m, "sync", platform=platform)
		add_clock(m, "sync_1e6", platform=platform)

		m.d.sync_1e6 += [
			i_unsync_buttons.pwr.eq(platform.request("button_pwr", 0)),
			i_unsync_buttons.fireA.eq(platform.request("button_fire", 0)),
			i_unsync_buttons.fireB.eq(platform.request("button_fire", 1)),
			i_unsync_buttons.up.eq(platform.request("button_up", 0)),
			i_unsync_buttons.down.eq(platform.request("button_down", 0)),
			i_unsync_buttons.left.eq(platform.request("button_left", 0)),
			i_unsync_buttons.right.eq(platform.request("button_right", 0)),
		]
		self.i_buttons = Record.like(i_unsync_buttons)
		m.submodules.i_button_ffsync = FFSynchronizer(i_unsync_buttons, self.i_buttons) # useful?

		
		# cd_sync = ClockDomain("sync")
		# m.d.comb += cd_sync.clk.eq(clk25)
		# m.domains += cd_sync
		# platform.add_clock_constraint(cd_sync.clk,  platform.default_clk_frequency)

		# external logic analyser, if desired
		if False:
			o_digital_discovery = platform.request("digital_discovery")
			m.d.sync += [
				o_digital_discovery.bus[0].eq(self.esp32.gpio5_cs), 	# cs
				o_digital_discovery.bus[1].eq(self.esp32.gpio16_sclk),	# clk
				o_digital_discovery.bus[2].eq(self.esp32.gpio4_copi),	# mosi
				o_digital_discovery.bus[3].eq(self.esp32.gpio12_cipo)	# miso
			]

		######## setup esp32 interaction ######

		# route the esp32's uart
		m.d.sync += [
			self.esp32.tx.eq(io_uart.rx),
			io_uart.tx.eq(self.esp32.rx),
		]

		# implement the esp32's reset/boot requirements
		with m.If((io_uart.dtr.i == 1) & (io_uart.rts.i == 1)):
			m.d.sync += self.esp32.en.eq(1 & ~self.i_buttons.pwr) 
			m.d.sync += self.esp32.gpio0.o.eq(1)
		with m.Elif((io_uart.dtr == 0) & (io_uart.rts == 0)):
			m.d.sync += self.esp32.en.eq(1 & ~self.i_buttons.pwr)
			m.d.sync += self.esp32.gpio0.o.eq(1)
		with m.Elif((io_uart.dtr == 1) & (io_uart.rts == 0)):
			m.d.sync += self.esp32.en.eq(0 & ~self.i_buttons.pwr)
			m.d.sync += self.esp32.gpio0.o.eq(1)
		with m.Elif((io_uart.dtr == 0) & (io_uart.rts == 1)):
			m.d.sync += self.esp32.en.eq(1 & ~self.i_buttons.pwr)
			m.d.sync += self.esp32.gpio0.o.eq(0)

		return m#, platform # note returning platform here is not standard
		