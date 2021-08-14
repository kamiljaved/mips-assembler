from ins import Instruction

class MIPSCompiler(object):

    STATUS_COMPILED = 0
    STATUS_COMPILED_WITH_WARNINGS = 1
    STATUS_COMPILED_WITH_ERRORS = 2
    STATUS_COMPILED_WITH_ERRORS_WARNINGS = 2
    STATUS_NOTCOMPILED_WITH_WARNINGS = 4
    STATUS_NOTCOMPILED_WITH_ERRORS = 5
    STATUS_NOTCOMPILED_WITH_ERRORS_WARNINGS = 6

    @staticmethod
    def Assembly2Binary(assembly_text, startaddress=0):
        assembly_lines = assembly_text.split('\n')
        instructions = []
        errors = []
        n = 0
        l = 0
        for line in assembly_lines:
            l += 1
            line = line.split("#")[0].strip()
            if len(line) == 0:
                continue
            sp = line.split(':')
            
            label = ""
            ins = ""
            if len(sp) == 1:
                ins = sp[0].split("#")[0].strip()
                if len(ins) != 0:
                    instructions.append(Instruction(ins, n, l, addroffset=startaddress))
            elif len(sp) == 2:
                label = sp[0].strip()
                ins = sp[1].split("#")[0].strip()
                if len(ins) != 0:
                    instructions.append(Instruction(ins, n, l, label, addroffset=startaddress))
            n += 1

        labelled = {}

        for ins in instructions:
            if ins.label != '':
                labelled[ins.label] = ins

        ins_block = int(Instruction.INSTRUCTION_SIZE/(Instruction.MEMORY_ALIGNMENT*8))

        for ins in instructions:
            if ins.ok:
                if ins.type=='R':
                    # set opcode
                    ins.binary['opcode'] = Instruction.opcodes['R']
                    # extract rs
                    rs = ins.assembly['rs']
                    rs = int(rs.split(Instruction.REGISTER_PREFIX)[1])
                    rs = MIPSCompiler.Decimal2Binary(rs, Instruction.formats_B['R']['rs'])
                    ins.binary['rs'] = rs
                    # extract rt
                    rt = ins.assembly['rt']
                    rt = int(rt.split(Instruction.REGISTER_PREFIX)[1])
                    rt = MIPSCompiler.Decimal2Binary(rt, Instruction.formats_B['R']['rt'])
                    ins.binary['rt'] = rt
                    # extract rd
                    rd = ins.assembly['rd']
                    rd = int(rd.split(Instruction.REGISTER_PREFIX)[1])
                    rd = MIPSCompiler.Decimal2Binary(rd, Instruction.formats_B['R']['rd'])
                    ins.binary['rd'] = rd
                    # set shamt
                    ins.binary['shamt'] = MIPSCompiler.Decimal2Binary(0, Instruction.formats_B['R']['shamt']) 
                    # set funct        
                    ins.binary['funct'] = Instruction.R_functs[ins.assembly['opcode']]
                elif ins.type=='I':
                    # set opcode
                    ins.binary['opcode'] = Instruction.opcodes[ins.assembly['opcode']]
                    # extract rs
                    rs = ins.assembly['rs']
                    rs = int(rs.split(Instruction.REGISTER_PREFIX)[1])
                    rs = MIPSCompiler.Decimal2Binary(rs, Instruction.formats_B['R']['rs'])
                    ins.binary['rs'] = rs
                    # extract rt
                    rt = ins.assembly['rt']
                    rt = int(rt.split(Instruction.REGISTER_PREFIX)[1])
                    rt = MIPSCompiler.Decimal2Binary(rt, Instruction.formats_B['R']['rt'])
                    ins.binary['rt'] = rt
                    # set immediate
                    imm = ins.assembly['immediate']
                    if ins.assembly['opcode'] in Instruction.branch:
                        ### branch
                        if imm in labelled:
                            # target address
                            imm = MIPSCompiler.Decimal2Binary(int((labelled[imm].address - ins.address - ins_block)/ins_block), Instruction.formats_B['I']['immediate'])
                        else:
                            ins.AddError(Instruction.ERR_1, imm)
                            ins.ok = False
                            errors.append(ins.error)
                    else:
                        ### immediate value
                        imm = MIPSCompiler.Decimal2Binary(int(imm), Instruction.formats_B['I']['immediate'])
                    ins.binary['immediate'] = imm
                elif ins.type=='J':
                    # set opcode
                    ins.binary['opcode'] = Instruction.opcodes[ins.assembly['opcode']]
                    # set immediate
                    imm = ins.assembly['immediate']
                    ### branch
                    if imm in labelled:
                        # target address
                        addr = MIPSCompiler.Decimal2Binary(int(labelled[imm].address/ins_block), Instruction.formats_B['J']['immediate'])
                        ins.binary['immediate'] = addr
                    else:
                        ins.AddError(Instruction.ERR_1, imm)
                        ins.ok = False
                        errors.append(ins.error)
                elif ins.type=='BI':
                    # set opcode
                    ins.binary['opcode'] = Instruction.opcodes[ins.assembly['opcode']]
                    # extract rt
                    rt = ins.assembly['rt']
                    rt = int(rt.split(Instruction.REGISTER_PREFIX)[1])
                    rt = MIPSCompiler.Decimal2Binary(rt, Instruction.formats_B['R']['rt'])
                    ins.binary['rt'] = rt
                    # set immediate
                    imm = ins.assembly['immediate']
                    if ins.assembly['opcode'] in Instruction.branch:
                        ### branch
                        if imm in labelled:
                            # target address
                            imm = MIPSCompiler.Decimal2Binary(int((labelled[imm].address - ins.address - ins_block)/ins_block), Instruction.formats_B['BI']['immediate1'] + Instruction.formats_B['BI']['immediate2'])                      
                        else:
                            ins.AddError(Instruction.ERR_1, imm)
                            ins.ok = False
                            errors.append(ins.error)    
                    else:
                        ### immediate value
                        imm = MIPSCompiler.Decimal2Binary(int(imm), Instruction.formats_B['BI']['immediate1'] + Instruction.formats_B['BI']['immediate2'])
                    ins.binary['immediate2'] = imm[0:Instruction.formats_B['BI']['immediate2']]
                    ins.binary['immediate1'] = imm[Instruction.formats_B['BI']['immediate2']:Instruction.formats_B['BI']['immediate2']+Instruction.formats_B['BI']['immediate1']]
            else:
                errors.append(ins.error)

        ins_dict = {}
        for ins in instructions:
            ins_dict[ins.num] = {}
            ins_dict[ins.num]["address"] = ins.address
            ins_dict[ins.num]["label"] = ins.label
            ins_dict[ins.num]["type"] = ins.type
            ins_dict[ins.num]["assembly"] = ins.assembly
            ins_dict[ins.num]["binary"] = ins.binary
            ins_dict[ins.num]["error"] = ins.error
        
        if len(errors) != 0:
            return MIPSCompiler.STATUS_NOTCOMPILED_WITH_ERRORS, errors,ins_dict

        compiled = MIPSCompiler.GenerateVerilog(instructions)
        return MIPSCompiler.STATUS_COMPILED, compiled, ins_dict

    @staticmethod
    def GenerateVerilog(instructions):
        verilog_ins = ""

        for ins in instructions:
            if ins.assembly['opcode'] is 'jalr':
                print(ins.assembly)
            if ins.label is "": 
                verilog_ins += f"// {ins.text} \n" 
            else: 
                verilog_ins += f"// {ins.label}: {ins.text} \n"
            block = int(Instruction.INSTRUCTION_SIZE/(Instruction.MEMORY_ALIGNMENT*8))

            verilog_ins += '{'
            w = 0
            for i in range(ins.address+block, ins.address, -1):
                verilog_ins += f'mem[{i-1}]'
                w += 1
                if w==block:
                    continue
                verilog_ins += ", "

            verilog_ins += '} = {'
            w = 0
            for val in ins.binary:            
                verilog_ins += f"{Instruction.formats_B[ins.type][val]}'b{ins.binary[val]}"
                w += 1
                if w==len(ins.binary):
                    continue
                verilog_ins += ", "

            verilog_ins += '};\n'

        return verilog_ins

    @staticmethod
    def Decimal2Binary(num, bits):

        x = abs(num)
        bin = ""
        while x > 0:
            bin = str(x%2) + bin
            x = int(x/2)
        while bits > len(bin):
            bin = "0" + bin
        if bits < len(bin):
            return 
        neg = ""
        if num < 0:        
            invert = False
            for i in range(len(bin)-1, -1, -1):
                if invert == True:
                    if bin[i] == '1':
                        neg = '0' + neg
                    else:
                        neg = '1' + neg
                else:
                    neg = bin[i] + neg
                if bin[i] == '1':
                    invert = True
            bin = neg

        return bin
