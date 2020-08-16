"""CPU functionality."""

import sys

TGREEN =  '\033[32m'
TRED = '\033[31m'
TYELLOW = '\033[33m'
ENDC = '\033[m'

HLT = 0b00000001 
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000 
RET = 0b00010001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.sp = 0xF4
                
    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) < 2:
            print(TRED + 'File to open is: "examples/mult.ls8"', ENDC)
            sys.exit()
        try: 
            with open(sys.argv[1]) as file:
                for instruction in file:
                    inst = instruction.split("#")[0].strip()
                    if inst == '':
                        continue
                    self.ram[address] = int(inst, 2)
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} not found.')    
  
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == MULT:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR
    
    def run(self):
        """Run the CPU."""
        pc = self.pc
        running = self.running
        sp = self.sp
        regs = self.reg
        regs[7] = sp
        
        while running:
            IR = self.ram_read(pc)
            operand_a = self.ram_read(pc + 1)
            operand_b = self.ram_read(pc + 2)    
            add_to_counter = (IR >> 6) + 1
        
            if IR >> 5 & 0b001:
                self.alu(IR, operand_a, operand_b)
            else: 
                if IR == LDI:
                    regs[operand_a] = operand_b           
                if IR == PRN:
                    print(TGREEN + str(regs[operand_a]) + ENDC, end=' => ' )
                if IR == PUSH:
                    regs[7] -= 1
                    sp = regs[7]
                    self.ram[sp] = regs[operand_a]
                if IR == POP:
                    sp = regs[7]
                    regs[operand_a] = self.ram[sp]
                    regs[7] += 1
                if IR == CALL:
                    NEXT_IR = pc + (IR >> 6) + 1
                    regs[7] -= 1
                    sp = regs[7]
                    self.ram[sp] = NEXT_IR              
                    pc = regs[operand_a]
                if IR == RET:
                    sp = regs[7]
                    regs[7] += 1                    
                    pc = self.ram[sp]     
                if IR == HLT:
                    print(TYELLOW + "Program halted." + ENDC)
                    running = False
            
            if not (IR >> 4) & 0b001:
                pc += add_to_counter 