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
  reg [31:0] PI_reload;
  reg [0:0] PI_ui__start;
  reg [0:0] PI_sync_1e6_rst;
  reg [0:0] PI_sync_1e6_clk;
  top UUT (
    .reload(PI_reload),
    .ui__start(PI_ui__start),
    .sync_1e6_rst(PI_sync_1e6_rst),
    .sync_1e6_clk(PI_sync_1e6_clk)
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
    UUT.dut.debug__count = 32'b00000000000000000000000000000000;
    UUT.dut.debug__count$4 = 32'b00000000000000000000000000000000;
    UUT.dut.delayer.counter_out = 32'b00000000000000000000000000000000;
    UUT.dut.delayer.fsm_state = 2'b01;
    UUT.dut.delayer_start = 1'b0;
    UUT.dut.ui__active = 1'b0;
    UUT.dut.ui__active$3 = 1'b0;
    UUT.dut.ui__done = 1'b0;
    UUT.dut.ui__done$2 = 1'b0;
    UUT.dut.ui__start$1 = 1'b0;
    UUT.dut_ui__start = 1'b0;
    UUT.ui__done$2 = 1'b0;
    UUT.ui__start$1 = 1'b0;

    // state 0
    PI_reload = 32'b10000000000000000000000000000000;
    PI_ui__start = 1'b1;
    PI_sync_1e6_rst = 1'b0;
    PI_sync_1e6_clk = 1'b0;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 2
    if (cycle == 1) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 3
    if (cycle == 2) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 4
    if (cycle == 3) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b1;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 5
    if (cycle == 4) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 6
    if (cycle == 5) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 7
    if (cycle == 6) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 8
    if (cycle == 7) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b1;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 9
    if (cycle == 8) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 10
    if (cycle == 9) begin
      PI_reload <= 32'b00000000000000000000000001000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 11
    if (cycle == 10) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 12
    if (cycle == 11) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 13
    if (cycle == 12) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 14
    if (cycle == 13) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 15
    if (cycle == 14) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 16
    if (cycle == 15) begin
      PI_reload <= 32'b00000000000000000000000001000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 17
    if (cycle == 16) begin
      PI_reload <= 32'b00000000000000000000000000000110;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 18
    if (cycle == 17) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 19
    if (cycle == 18) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 20
    if (cycle == 19) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 21
    if (cycle == 20) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 22
    if (cycle == 21) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 23
    if (cycle == 22) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 24
    if (cycle == 23) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 25
    if (cycle == 24) begin
      PI_reload <= 32'b00000000000000000000000000000100;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 26
    if (cycle == 25) begin
      PI_reload <= 32'b00000000000000000000000000010110;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 27
    if (cycle == 26) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 28
    if (cycle == 27) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 29
    if (cycle == 28) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 30
    if (cycle == 29) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 31
    if (cycle == 30) begin
      PI_reload <= 32'b00000000000000000000000000000100;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 32
    if (cycle == 31) begin
      PI_reload <= 32'b00000000000000000000000000000101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 33
    if (cycle == 32) begin
      PI_reload <= 32'b00000000000000000000000000100001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 34
    if (cycle == 33) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 35
    if (cycle == 34) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 36
    if (cycle == 35) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 37
    if (cycle == 36) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 38
    if (cycle == 37) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 39
    if (cycle == 38) begin
      PI_reload <= 32'b00000000000000000000000000001111;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 40
    if (cycle == 39) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 41
    if (cycle == 40) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 42
    if (cycle == 41) begin
      PI_reload <= 32'b00000000000000000000000000011110;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 43
    if (cycle == 42) begin
      PI_reload <= 32'b00000000000000000000000000000101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 44
    if (cycle == 43) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 45
    if (cycle == 44) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 46
    if (cycle == 45) begin
      PI_reload <= 32'b00000000000000000000000000000101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 47
    if (cycle == 46) begin
      PI_reload <= 32'b00000000000000000000000000000100;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 48
    if (cycle == 47) begin
      PI_reload <= 32'b00000000000000000000000000100000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 49
    if (cycle == 48) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 50
    if (cycle == 49) begin
      PI_reload <= 32'b00000000000000000000000000110010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 51
    if (cycle == 50) begin
      PI_reload <= 32'b00000000000000000000000000100101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 52
    if (cycle == 51) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 53
    if (cycle == 52) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 54
    if (cycle == 53) begin
      PI_reload <= 32'b00000000000000000000000000000100;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 55
    if (cycle == 54) begin
      PI_reload <= 32'b00000000000000000000000000011111;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 56
    if (cycle == 55) begin
      PI_reload <= 32'b00000000000000000000000000100010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 57
    if (cycle == 56) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 58
    if (cycle == 57) begin
      PI_reload <= 32'b00000000000000000000000000011011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 59
    if (cycle == 58) begin
      PI_reload <= 32'b00000000000000000000000000100001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 60
    if (cycle == 59) begin
      PI_reload <= 32'b00000000000000000000000000100010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 61
    if (cycle == 60) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 62
    if (cycle == 61) begin
      PI_reload <= 32'b00000000000000000000000000001001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 63
    if (cycle == 62) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 64
    if (cycle == 63) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 65
    if (cycle == 64) begin
      PI_reload <= 32'b00000000000000000000000000010011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 66
    if (cycle == 65) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 67
    if (cycle == 66) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 68
    if (cycle == 67) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 69
    if (cycle == 68) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 70
    if (cycle == 69) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 71
    if (cycle == 70) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 72
    if (cycle == 71) begin
      PI_reload <= 32'b00000000000000000000000000000110;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 73
    if (cycle == 72) begin
      PI_reload <= 32'b00000000000000000000000000011010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 74
    if (cycle == 73) begin
      PI_reload <= 32'b00000000000000000000000000011110;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 75
    if (cycle == 74) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 76
    if (cycle == 75) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 77
    if (cycle == 76) begin
      PI_reload <= 32'b00000000000000000000000000011011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 78
    if (cycle == 77) begin
      PI_reload <= 32'b00000000000000000000000000000001;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 79
    if (cycle == 78) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 80
    if (cycle == 79) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 81
    if (cycle == 80) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 82
    if (cycle == 81) begin
      PI_reload <= 32'b00000000000000000000000000010000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 83
    if (cycle == 82) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 84
    if (cycle == 83) begin
      PI_reload <= 32'b00000000000000000000000000010000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 85
    if (cycle == 84) begin
      PI_reload <= 32'b00000000000000000000000000010011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 86
    if (cycle == 85) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 87
    if (cycle == 86) begin
      PI_reload <= 32'b00000000000000000000000000000100;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 88
    if (cycle == 87) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 89
    if (cycle == 88) begin
      PI_reload <= 32'b00000000000000000000000001000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 90
    if (cycle == 89) begin
      PI_reload <= 32'b00000000000000000000000000001010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 91
    if (cycle == 90) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 92
    if (cycle == 91) begin
      PI_reload <= 32'b00000000000000000000000000001000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 93
    if (cycle == 92) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 94
    if (cycle == 93) begin
      PI_reload <= 32'b00000000000000000000000000001000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 95
    if (cycle == 94) begin
      PI_reload <= 32'b00000000000000000000000000000101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 96
    if (cycle == 95) begin
      PI_reload <= 32'b00000000000000000000000000000101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 97
    if (cycle == 96) begin
      PI_reload <= 32'b10000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 98
    if (cycle == 97) begin
      PI_reload <= 32'b00000000000000000000000000000110;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 99
    if (cycle == 98) begin
      PI_reload <= 32'b00000000000000000000000000000101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 100
    if (cycle == 99) begin
      PI_reload <= 32'b00000000000000000000000000000100;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 101
    if (cycle == 100) begin
      PI_reload <= 32'b00000000000000000000000000000011;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 102
    if (cycle == 101) begin
      PI_reload <= 32'b00000000000000000000000000000010;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 103
    if (cycle == 102) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 104
    if (cycle == 103) begin
      PI_reload <= 32'b00000000000000000000000001100101;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 105
    if (cycle == 104) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 106
    if (cycle == 105) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    // state 107
    if (cycle == 106) begin
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
      PI_sync_1e6_rst <= 1'b0;
      PI_sync_1e6_clk <= 1'b0;
    end

    genclock <= cycle < 107;
    cycle <= cycle + 1;
  end
endmodule
