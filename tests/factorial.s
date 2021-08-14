fact:   addi sp, sp, -8      # adjust stack for 2 items    
sw x30, 4(sp)                   # save the return address    
sw x10, 0(sp)                  # save the argument n

addi   x11, x10, -1              # x11 = n - 1 
bge   x11, x0, L1                # if (n - 1) >= 0, go to L1

addi  x10, x0, 1                # return 1 
addi  sp, sp, 8              # pop 2 items off stack 
jalr  x0, 0(x30)                 # return to caller

L1: addi x10, x10, -1           # n >= 1: argument gets (n − 1)      
jal x30, fact                    # call fact with (n − 1)

addi  x12, x10, 0                #  return from jal: move result of fact (n - 1) to x12: 
lw  x10, 0(sp)                  # restore argument n 
lw  x30, 4(sp)                   # restore the return address 
addi  sp, sp, 8                # adjust stack pointer to pop 2 items
mul   x10, x10, x12              # return n * fact (n − 1)
jalr   x0, 0(x30)                # return to the caller
