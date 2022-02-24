attribute \generator "Amaranth"
attribute \amaranth.hierarchy "top.adder"
module \adder
  attribute \src "test1_amlib_timers.py:159"
  wire width 8 output 0 \out
  attribute \src "test1_amlib_timers.py:157"
  wire width 8 input 1 \x
  attribute \src "test1_amlib_timers.py:158"
  wire width 8 input 2 \y
  attribute \src "test1_amlib_timers.py:165"
  wire width 9 $1
  attribute \src "test1_amlib_timers.py:165"
  wire width 9 $2
  attribute \src "test1_amlib_timers.py:165"
  cell $add $3
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 8
    parameter \Y_WIDTH 9
    connect \A \x
    connect \B \y
    connect \Y $2
  end
  connect $1 $2
  process $group_0
    assign \out 8'00000000
    assign \out $1 [7:0]
    sync init
  end
end
attribute \generator "Amaranth"
attribute \top 1
attribute \amaranth.hierarchy "top"
module \top
  attribute \src "test1_amlib_timers.py:157"
  wire width 8 input 0 \x
  attribute \src "test1_amlib_timers.py:158"
  wire width 8 input 1 \y
  attribute \src "test1_amlib_timers.py:159"
  wire width 8 output 2 \out
  cell \adder \adder
    connect \out \out
    connect \x \x
    connect \y \y
  end
  attribute \src "test1_amlib_timers.py:181"
  wire width 1 $assert$en
  attribute \src "test1_amlib_timers.py:181"
  wire width 1 $assert$check
  attribute \src "test1_amlib_timers.py:181"
  wire width 11 $1
  attribute \src "test1_amlib_timers.py:181"
  wire width 10 $2
  attribute \src "test1_amlib_timers.py:181"
  cell $mul $3
    parameter \A_SIGNED 0
    parameter \A_WIDTH 2
    parameter \B_SIGNED 0
    parameter \B_WIDTH 8
    parameter \Y_WIDTH 10
    connect \A 2'10
    connect \B \x
    connect \Y $2
  end
  attribute \src "test1_amlib_timers.py:181"
  wire width 11 $4
  attribute \src "test1_amlib_timers.py:181"
  cell $add $5
    parameter \A_SIGNED 0
    parameter \A_WIDTH 10
    parameter \B_SIGNED 0
    parameter \B_WIDTH 8
    parameter \Y_WIDTH 11
    connect \A $2
    connect \B \y
    connect \Y $4
  end
  connect $1 $4
  attribute \src "test1_amlib_timers.py:181"
  wire width 1 $6
  attribute \src "test1_amlib_timers.py:181"
  cell $eq $7
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 8
    parameter \Y_WIDTH 1
    connect \A \out
    connect \B $1 [7:0]
    connect \Y $6
  end
  attribute \src "test1_amlib_timers.py:181"
  cell $assert $8
    connect \A $assert$check
    connect \EN $assert$en
  end
  process $group_0
    assign $assert$en 1'0
    assign $assert$check 1'0
    assign $assert$check $6
    assign $assert$en 1'1
    sync init
  end
  attribute \src "test1_amlib_timers.py:185"
  wire width 1 $assume$en
  attribute \src "test1_amlib_timers.py:185"
  wire width 1 $assume$check
  attribute \src "test1_amlib_timers.py:185"
  wire width 9 $9
  attribute \src "test1_amlib_timers.py:185"
  cell $sshl $10
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 9
    connect \A \y
    connect \B 1'1
    connect \Y $9
  end
  attribute \src "test1_amlib_timers.py:185"
  wire width 1 $11
  attribute \src "test1_amlib_timers.py:185"
  cell $eq $12
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 9
    parameter \Y_WIDTH 1
    connect \A \x
    connect \B $9
    connect \Y $11
  end
  attribute \src "test1_amlib_timers.py:185"
  cell $assume $13
    connect \A $assume$check
    connect \EN $assume$en
  end
  process $group_2
    assign $assume$en 1'0
    assign $assume$check 1'0
    assign $assume$check $11
    assign $assume$en 1'1
    sync init
  end
  attribute \src "test1_amlib_timers.py:188"
  wire width 1 $cover$en
  attribute \src "test1_amlib_timers.py:188"
  wire width 1 $cover$check
  attribute \src "test1_amlib_timers.py:187"
  wire width 9 $14
  attribute \src "test1_amlib_timers.py:187"
  cell $sshl $15
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 9
    connect \A \y
    connect \B 1'1
    connect \Y $14
  end
  attribute \src "test1_amlib_timers.py:187"
  wire width 1 $16
  attribute \src "test1_amlib_timers.py:187"
  cell $eq $17
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 9
    parameter \Y_WIDTH 1
    connect \A \x
    connect \B $14
    connect \Y $16
  end
  attribute \src "test1_amlib_timers.py:188"
  wire width 1 $18
  attribute \src "test1_amlib_timers.py:188"
  cell $gt $19
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 1
    connect \A \out
    connect \B 1'0
    connect \Y $18
  end
  attribute \src "test1_amlib_timers.py:188"
  wire width 1 $20
  attribute \src "test1_amlib_timers.py:188"
  cell $lt $21
    parameter \A_SIGNED 0
    parameter \A_WIDTH 8
    parameter \B_SIGNED 0
    parameter \B_WIDTH 7
    parameter \Y_WIDTH 1
    connect \A \out
    connect \B 7'1000000
    connect \Y $20
  end
  attribute \src "test1_amlib_timers.py:188"
  wire width 1 $22
  attribute \src "test1_amlib_timers.py:188"
  cell $and $23
    parameter \A_SIGNED 0
    parameter \A_WIDTH 1
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 1
    connect \A $18
    connect \B $20
    connect \Y $22
  end
  attribute \src "test1_amlib_timers.py:188"
  cell $cover $24
    connect \A $cover$check
    connect \EN $cover$en
  end
  process $group_4
    assign $cover$en 1'0
    assign $cover$check 1'0
    attribute \src "test1_amlib_timers.py:187"
    switch { $16 }
      attribute \src "test1_amlib_timers.py:187"
      case 1'1
        assign $cover$check $22
        assign $cover$en 1'1
    end
    sync init
  end
end

