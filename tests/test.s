
# R-TYPE: Arithmetic
R_type: add x3, x1, x2      # add
        sub x3, x1, x2      # subtract
        mul x3, x1, x2      # multiply
        and x3, x1, x2      # bitwise and
        or  x3, x1, x2      # bitwise or
        slt x3, x1, x2      # set on less than
        nor x3, x1, x2      # bitwise nor
        xor x3, x1, x2      # bitwise xor
        sll x3, x1, x2      # shift-left logical
        srl x3, x1, x2      # shift-right logical

# I-TYPE: Arithmetic
I_type: addi x3, x1, 5      # add-immediate

# I-TYPE: Load and Store
Load:   lw x3, 0(x4)        # load word
Store:  sw x3, 4(x4)        # store word

# I-TYPE: Branch
Br1:    beq x5, x6, Jump    # branch if equal
Br2:    bne x5, x6, Br4     # branch if not-equal
Br3:    add x6, x5, x0
        bge x5, x0, Br1     # branch if greater-than/equal
Br4:    blt x6, x5, Br3     # branch if less-than

# J-TYPE: Jump
Jump:   j R_type            # jump to label/address
 