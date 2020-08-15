"""CPU functionality."""
import sys
class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7 # SP is R7
        self.fl = 0
    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2: 
            print("Need file name!")
            sys.exit(1)  
        try: 
            address = 0
            with open(sys.argv[1]) as f:
                for line in f: 
                    comment_split = line.split("#")
                    value = comment_split[0].strip()
                    if value == "":
                        continue
                    num = int(value, 2)
                    #print(f"{num:08b}: {num}")
                    #print(value)
                    self.ram[address] = num
                    #print(address)
                    address += 1
        except FileNotFoundError: 
            print("File not found!")  
            sys.exit(2)      
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]    
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:  
                self.fl = self.fl | 1 
            elif self.reg[reg_a] > self.reg[reg_b]: 
                self.fl = self.fl | 2 
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = self.fl | 4 
        else:
            raise Exception("Unsupported ALU operation")
    def ram_read(self, mar):
        return self.ram[mar]   
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()
    def run(self):
        """Run the CPU."""
        # Halt CPU and exit emulator
        HLT = 0b00000001 
        # Set value of register to integer
        LDI = 0b10000010
        # Print numeric value stored in register
        PRN = 0b01000111
        # Multiply the values in two registers together and store the result in registerA
        MUL = 0b10100010
        # Push the value in the given register on the stack
        PUSH = 0b01000101
        # Pop the value at the top of the stack into the given register
        POP = 0b01000110
        # Calls a subroutine (function) at the address stored in the register
        CALL = 0b01010000
        # Pop the value from the top of the stack and store it in the PC
        RET = 0b00010001
        # Add regA and regB
        ADD = 0b10100000
        # Compare the values in two registers.
        CMP = 0b10100111
        # Jump to the address stored in the given register.
        JMP = 0b01010100
        # If equal flag is set (true), jump to the address stored in the given register.
        JEQ = 0b01010101
        # If E flag is clear (false, 0), jump to the address stored in the given register.
        JNE = 0b01010110
        # Perform a bitwise-NOT on the value in a register, storing the result in the register.
        NOT = 0b01101001
        running = True
        while running: 
            ir = self.ram_read(self.pc)
            #print(ir)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if ir == PRN: 
                print(self.reg[operand_a])
                self.pc += 2
            elif ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif ir == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3    
            elif ir == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3     
            elif ir == HLT:
                running = False
                sys.exit(1)       
            elif ir == PUSH:
                #Decrement the sp.
                self.reg[self.sp] -= 1
                # Copy the value in the given register to the address pointed to by sp
                val = self.reg[operand_a]
                self.ram[self.reg[self.sp]] = val
                self.pc += 2
                # print(self.ram)
                # print(self.reg)
            elif ir == POP:
                # Grab value from the top of the stack
                reg = operand_a
                val = self.ram[self.reg[self.sp]]    
                # Copy the value from the address pointed to by sp to the given register
                self.reg[reg] = val
                # Increment sp
                self.reg[self.sp] += 1
                self.pc += 2
                # print(self.ram)
                # print(self.reg)
            elif ir == CALL:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[operand_a]
            elif ir == RET:
                val = self.ram[self.reg[self.sp]] 
                self.pc = val
                self.reg[self.sp] += 1    
            elif ir == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
            elif ir == NOT:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3    
            elif ir == JMP:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[operand_a]
            elif ir == JEQ:
                if self.fl == 1 or self.fl == 3 or self.fl == 7 or self.fl == 5: 
                    self.reg[self.sp] -= 1
                    self.ram[self.reg[self.sp]] = self.pc + 2
                    self.pc = self.reg[operand_a]
                else: 
                    self.pc += 2        
            elif ir == JNE:
                if self.fl == 0 or self.fl == 2 or self.fl == 3 or self.fl == 4: 
                    self.reg[self.sp] -= 1
                    self.ram[self.reg[self.sp]] = self.pc + 2
                    self.pc = self.reg[operand_a]
                else: 
                    self.pc += 2 