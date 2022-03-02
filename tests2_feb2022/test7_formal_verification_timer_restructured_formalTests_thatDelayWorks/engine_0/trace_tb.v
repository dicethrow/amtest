`ifndef VERILATOR
module testbench;
  reg [4095:0] vcdfile;
  reg clock;
`else
module testbench(input clock, output reg genclock);
  initial genclock = 1;
`endif
  reg genclock = 1;
  reg [31:0] cycle = 0;
  reg [0:0] PI__ui__tb_fanin_flags__in_start;
  reg [0:0] PI_ui__tb_fanout_flags__trigger;
  reg [11:0] PI_ui__load;
  reg [0:0] PI__ui__tb_fanin_flags__in_done;
  wire [0:0] PI_clk = clock;
  reg [0:0] PI_rst;
  top UUT (
    ._ui__tb_fanin_flags__in_start(PI__ui__tb_fanin_flags__in_start),
    .ui__tb_fanout_flags__trigger(PI_ui__tb_fanout_flags__trigger),
    .ui__load(PI_ui__load),
    ._ui__tb_fanin_flags__in_done(PI__ui__tb_fanin_flags__in_done),
    .clk(PI_clk),
    .rst(PI_rst)
  );
`ifndef VERILATOR
  initial begin
    if ($value$plusargs("vcd=%s", vcdfile)) begin
      $dumpfile(vcdfile);
      $dumpvars(0, testbench);
    end
    #5 clock = 0;
    while (genclock) begin
      #5 clock = 0;
      #5 clock = 1;
    end
  end
`endif
  initial begin
`ifndef VERILATOR
    #1;
`endif
    // UUT.$assert$check = 1'b0;
    // UUT.$assert$en = 1'b0;
    // UUT.$sample$s$init$sync$1 = 1'b0;
    // UUT.$sample$s$init$sync$10 = 1'b0;
    // UUT.$sample$s$init$sync$11 = 1'b0;
    // UUT.$sample$s$init$sync$12 = 1'b0;
    // UUT.$sample$s$init$sync$13 = 1'b0;
    // UUT.$sample$s$init$sync$14 = 1'b0;
    // UUT.$sample$s$init$sync$15 = 1'b0;
    // UUT.$sample$s$init$sync$16 = 1'b0;
    // UUT.$sample$s$init$sync$17 = 1'b0;
    // UUT.$sample$s$init$sync$18 = 1'b0;
    // UUT.$sample$s$init$sync$19 = 1'b0;
    // UUT.$sample$s$init$sync$2 = 1'b0;
    // UUT.$sample$s$init$sync$20 = 1'b0;
    // UUT.$sample$s$init$sync$21 = 1'b0;
    // UUT.$sample$s$init$sync$22 = 1'b0;
    // UUT.$sample$s$init$sync$23 = 1'b0;
    // UUT.$sample$s$init$sync$3 = 1'b0;
    // UUT.$sample$s$init$sync$4 = 1'b0;
    // UUT.$sample$s$init$sync$5 = 1'b0;
    // UUT.$sample$s$init$sync$6 = 1'b0;
    // UUT.$sample$s$init$sync$7 = 1'b0;
    // UUT.$sample$s$init$sync$8 = 1'b0;
    // UUT.$sample$s$init$sync$9 = 1'b0;
    UUT._ui__done = 1'b0;
    UUT._ui__load = 12'b000000000000;
    UUT.delay_fsm_state = 2'b00;
    UUT.delayer._ui__done = 1'b0;
    UUT.delayer._ui__inactive = 1'b0;
    UUT.delayer._ui__load = 12'b000000000000;
    UUT.delayer.countdown = 12'b000000000000;
    UUT.delayer.ui__done = 1'b0;
    UUT.delayer.ui__inactive = 1'b0;
    UUT.delayer_ui__load = 12'b000000000000;
    UUT.timer_ought_to_finish = 1'b0;

    // state 0
    PI__ui__tb_fanin_flags__in_start = 1'b0;
    PI_ui__tb_fanout_flags__trigger = 1'b0;
    PI_ui__load = 12'b000000000000;
    PI__ui__tb_fanin_flags__in_done = 1'b0;
    PI_rst = 1'b0;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 2
    if (cycle == 1) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000001;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 3
    if (cycle == 2) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 4
    if (cycle == 3) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000010000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 5
    if (cycle == 4) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 6
    if (cycle == 5) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 7
    if (cycle == 6) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 8
    if (cycle == 7) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 9
    if (cycle == 8) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    // state 10
    if (cycle == 9) begin
      PI__ui__tb_fanin_flags__in_start <= 1'b0;
      PI_ui__tb_fanout_flags__trigger <= 1'b0;
      PI_ui__load <= 12'b000000000000;
      PI__ui__tb_fanin_flags__in_done <= 1'b0;
      PI_rst <= 1'b0;
    end

    genclock <= cycle < 10;
    cycle <= cycle + 1;
  end
endmodule
