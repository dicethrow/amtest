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


class Clocky(Elaboratable):
	def __init__(self):
		self.x = Signal(7)
		self.load = Signal()
		self.value = Signal(7)

	def elaborate(self, platform: Platform) -> Module:
		m = Module()

		with m.If(self.load):
			m.d.sync += self.x.eq(Mux(self.value <= 100, self.value, 100))
		with m.Elif(self.x == 100):
			m.d.sync += self.x.eq(0)
		with m.Else():
			m.d.sync += self.x.eq(self.x + 1)
		
		return m

	def ports(self) -> List[Signal]:
		return [self.x, self.load, self.value]


if __name__ == "__main__":
	from pathlib import Path
	current_filename = str(Path(__file__).absolute()).split(".py")[0]

	parser = main_parser()
	args = parser.parse_args()

	if args.action == "generate":

		# following the n8000 tutorial project docs
		# This is called 'formal verification'
		# where the simulator tests all conditions (within specified limits) that:
		# 	- are universally true (asserts). If a fail occurs, then show an example waveform.
		# 	- are valid for some condition (cover). Show a waveform that matches these.
		#		Note that the use of m.If() focusses the states of the cover below uses.
		# 	- match some assumptions.(Assume) This may be good to remove some illegal states.
		#	  Reduces the input
		# main_runner generates the output that will be run through yosys

		with open(current_filename+".sby", "w") as sby_file:
			# Why depth=2?
			file_content = f"""
			[tasks]
			cover
			bmc

			[options]
			bmc: mode bmc
			cover: mode cover
			depth 40
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
		
		m = Module()
		m.submodules.clocky = clocky = Clocky()

		rst = ResetSignal()
		clk = ClockSignal()


		def sync_formal_verification():
			def that_clock_increments():
				# and that no value will be loaded in at t=0
				with m.If((clocky.x > 0) & (Past(clocky.load) == 0)):
					m.d.sync += Assert(clocky.x == (Past(clocky.x) + 1)[:7])

			def that_rollover_occurs_at_100():
				# In the case when we may have just rolled over,
				with m.If(clocky.x == 0):
					# and that the clock domain hasn't just been reset
					with m.If(~Past(rst)):
						# and that we haven't just loaded zero 
						with m.If(~Past(clocky.load)):
							# ensure that the previous value was 100
							m.d.sync += Assert(Past(clocky.x) == 100)

			def that_load_works():
				# that the clock domain hasn't just been reset
				with m.If(~Past(rst)):
					with m.If(Past(clocky.load)):
						m.d.sync += Assert(clocky.x == Mux(
							Past(clocky.value)<=100,
							Past(clocky.value),
							100))

			def cover__can_clock_increment_to_3():
				# that the clock domain hasn't just been reset
				with m.If(~Past(rst)):
					# and that we haven't just loaded anything 
					with m.If(~Past(clocky.load)):
						# Can x get to 3, where the previous step is not a load?
						m.d.sync += Cover(clocky.x == 3) # cover: find inputs such that this is true. Note the 'depth 40' in the .sby file relates to the cycles requiried to get to this point
					

			def expected_behavior():
				""" this is too big to understand! 
				do smaller bits, like above """
				# if a reset just happened
				with m.If(Past(rst)):
					m.d.sync += Assert(clocky.x == 0)

				# not in reset,
				# normal clock operation
				with m.Else():
					# if a new value was loaded
					with m.If(Past(clocky.load)):

						# if the new value is less than the max
						next_value = Past(clocky.value)
						with m.If(next_value <= 0x64):
							m.d.sync += Assert(clocky.x == next_value)

						# otherwise this is what it should default to
						with m.Else():
							m.d.sync += Assert(clocky.x == 0x64)

					# normal clock incrementing operation
					with m.Else():

						# make sure incrementing works
						with m.If(Past(clocky.x) < 0x64):
							m.d.sync += Assert(clocky.x == (Past(clocky.x) + 1)[:7]) 
						
						# make sure the clock rolls over properly at 0x64 (100)
						with m.If(Past(clocky.x) == 0x64):
							m.d.sync += Assert(clocky.x == 0)

			expected_behavior()

			that_clock_increments()
			that_rollover_occurs_at_100()
			that_load_works()
			cover__can_clock_increment_to_3()

		sync_formal_verification() # formal verification with a clock domain

		# main_runner is only useful for outputting code to run through yosys
		# we don't use this when we use nmigen's native simulator
		main_runner(parser, args, m) 
	
	else:
		assert 0, "simulate or upload not implemented"