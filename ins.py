
class Instruction(object): 

    lists = { 
        'R':    ["add", "sub", "and", "or", "slt", "xor", "nor", "sll", "srl", "sra", "mul"],
        'I':    ["addi", "lw", "sw", "beq", "bne", "blt", "bge", "jalr", "lui"],
        'J':    ["jump", "j"],
        'BI':   ["jal", "li"],  # li is load immediate
    }
    
    branch =   ['beq', "bne", "blt", "bge", "jump", "j", "jal"]

    opcodes = {
        'R':    '000000',
        'addi': '000001',
        'lw':   '100011',
        'sw':   '101011',
        'beq':  '000100',
        'bne':  '000101',
        'blt':  '001000',
        'bge':  '001001',
        'jump': '000110', 
        'j':    '000110',
        'jal':  '001010',
        'jalr': '001011',
        'lui':  '001111',
    }

    R_functs = {
        'add':  '100000',
        'sub':  '100010',
        'mul':  '100011',
        'and':  '100100',
        'or':   '100101',
        'slt':  '101010',
        'nor':  '100110',
        'xor':  '100111',
        'sll':  '101000',
        'srl':  '101001',
    }

    formats_A = { 
        'R':    {"opcode":"", "rs":"", "rt":"", "rd":""},
        'I':    {"opcode":"", "rs":"", "rt":"", "immediate":""},
        'J':    {"opcode":"", "immediate":""},
        'BI':   {"opcode":"", "rt":"", "immediate":""},
    }
    
    formats_B = { 
        'R':    {"opcode":6, "rs":5, "rt":5, "rd":5, "shamt":5, "funct":6},
        'I':    {"opcode":6, "rs":5, "rt":5, "immediate":16},
        'J':    {"opcode":6, "immediate":26},
        'BI':   {"opcode":6, "immediate2":5, "rt":5, "immediate1":16},
    }

    invalid_labels = {
        'sp',
    }

    # Instruction Specifications
    INSTRUCTION_SIZE = 32   # in BITS
    MEMORY_ALIGNMENT = 1    # in BYTES
    MEMORY_NAME = "mem"
    # Register Information
    REGISTER_PREFIX = "x"
    REG_STACK_PTR = "x31"

    # Constructor 
    def __init__(self, text, num=0, line=0, label="", addroffset=0):

        self.text = text
        self.num = num
        self.line = line
        self.label = label.strip()
        self.type = ""
        self.assembly = {}
        self.binary = {}
        self.address = int((num+addroffset)*Instruction.INSTRUCTION_SIZE/(Instruction.MEMORY_ALIGNMENT*8))
        self.ok = True
        self.error = ""

        # check for invalid labels
        if self.label in Instruction.invalid_labels:
            self.AddError(Instruction.ERR_0, self.label)
            self.ok = False

        parts = text.split(' ')
        while '' in parts:
            parts.remove('')
        opcode = parts[0].strip()
        parts.remove(opcode)
        rest = ""
        for part in parts:
            rest += part
        operands = rest.split(',')

        for t in Instruction.lists:
            if opcode in Instruction.lists[t]:
                self.type = t
                self.assembly = Instruction.formats_A[self.type].copy()
                self.binary = Instruction.formats_B[self.type].copy()

        self.assembly['opcode'] = opcode

        if self.type is 'R' and len(operands)==(len(Instruction.formats_A['R'])-1):
            self.assembly['rd'] = operands[0].strip()
            self.assembly['rs'] = operands[1].strip()
            self.assembly['rt'] = operands[2].strip()
        elif self.type is 'I':
            if len(operands)==(len(Instruction.formats_A['I'])-1):      # eg. addi
                self.assembly['rt'] = operands[0].strip()
                self.assembly['rs'] = operands[1].strip()
                self.assembly['immediate'] = operands[2].strip()
            elif len(operands)==(len(Instruction.formats_A['I'])-2):    # eg. lw
                self.assembly['rt'] = operands[0].strip()
                if opcode == 'lui':                                     # exceptional case: lui
                    self.assembly['rs'] = 'x0'
                    self.assembly['immediate'] = operands[1].strip()
                else:
                    sp = operands[1].split('(')
                    self.assembly['rs'] = sp[1].split(')')[0].strip()
                    self.assembly['immediate'] = sp[0].strip()
        if self.type is 'J' and len(operands)==(len(Instruction.formats_A['J'])-1):
                self.assembly['immediate'] = operands[0].strip()
        if self.type is 'BI' and len(operands)==(len(Instruction.formats_A['BI'])-1):
                self.assembly['rt'] = operands[0].strip()
                self.assembly['immediate'] = operands[1].strip()

        # setup predefined registers
        for opr in self.assembly:
            if self.assembly[opr] == 'sp':
                self.assembly[opr] = Instruction.REG_STACK_PTR

    def getLabel(self):
        return self.label
    
    def getType(self):
        return self.type
        
    def setLabel(self, label):
        self.label = label
    
    def setType(self, instype):
        self.type = instype
    
    def addAddressOffset(self, offset):
        self.address += offset

    # Error Handling
    
    ERR_0 = "Bad label"
    ERR_1 = "No such label"

    def AddError(self, err, arg=None):
        if self.error == "":
            self.error = f'Line-{self.line}  ──  '
        else:
            self.error += f', '

        if arg is None:
            self.error += f'{err}'
        else:
            self.error += f'{err}: \'{arg}\''