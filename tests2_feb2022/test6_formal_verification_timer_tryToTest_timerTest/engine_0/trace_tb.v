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
  reg [0:0] PI_rst;
  wire [0:0] PI_clk = clock;
  reg [31:0] PI_reload;
  reg [0:0] PI_ui__start;
  top UUT (
    .rst(PI_rst),
    .clk(PI_clk),
    .reload(PI_reload),
    .ui__start(PI_ui__start)
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
    UUT.debug__count$4 = 32'b00000000000000000000000000000000;
    UUT.delayer.counter_out = 32'b00000000000000000000000000000000;
    UUT.delayer.fsm_state = 2'b01;
    UUT.delayer_start = 1'b0;
    UUT.ui__done$2 = 1'b0;
    UUT.ui__start$1 = 1'b0;

    // state 0
    PI_rst = 1'b0;
    PI_reload = 32'b10000000000000000000000000000000;
    PI_ui__start = 1'b0;
  end
  always @(posedge clock) begin
    // state 1
    if (cycle == 0) begin
      PI_rst <= 1'b0;
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
    end

    // state 2
    if (cycle == 1) begin
      PI_rst <= 1'b0;
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
    end

    // state 3
    if (cycle == 2) begin
      PI_rst <= 1'b0;
      PI_reload <= 32'b00000000000000000000000000000000;
      PI_ui__start <= 1'b0;
    end

    genclock <= cycle < 3;
    cycle <= cycle + 1;
  end
endmodule
