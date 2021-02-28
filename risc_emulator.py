#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bitarray import bitarray
import re

path = 'e:\\design_auto\\'
filename = 'machinecode.txt'
outfile_mem = 'data_mem.txt'
outfile_reg = 'reg.txt'


def binToInt(s, num):
    # s is the binary string, and num is the number of bits
    return int(s[1:], 2) - int(s[0]) * (1 << (num - 1))


def intToBin(i, num):
    # i is a int format number
    return (bin(((1 << num) - 1) & i)[2:]).zfill(num)


class regfile(object):

    def __init__(self):
        self.regfiles = {'x0': 32*'0', 'x1': 32*'0', 'x2': 32*'0', 'x3': 32*'0',
                         'x4': 32*'0', 'x5': 32*'0', 'x6': 32*'0', 'x7': 32*'0',
                         'x8': 32*'0', 'x9': 32*'0', 'x10': 32*'0', 'x11': 32*'0',
                         'x12': 32*'0', 'x13': 32*'0', 'x14': 32*'0', 'x15': 32*'0',
                         'x16': 32*'0', 'x17': 32*'0', 'x18': 32*'0', 'x19': 32*'0',
                         'x20': 32*'0', 'x21': 32*'0', 'x22': 32*'0', 'x23': 32*'0',
                         'x24': 32*'0', 'x25': 32*'0', 'x26': 32*'0', 'x27': 32*'0',
                         'x28': 32*'0', 'x29': 32*'0', 'x30': 32*'0', 'x31': 32*'0'}

    def set_reg_values(self, reg, values):
        # addr/values input are str and int respectively,such as ('31', 666)
        if not isinstance(reg, str):
            raise TypeError('bad operand type for reg')
        if not isinstance(values, int):
            raise TypeError('bad operand type for values')
        if reg == '0':
            raise ValueError('x0 can not be set')
        x_reg = 'x'+reg
        values = str(intToBin(values, 32))
        if x_reg in self.regfiles.keys():
            self.regfiles[x_reg] = values
        else:
            raise ValueError('reg number is out of range')

    def get_reg_values(self, reg):
        # reg is str,such as ('2')
        if not isinstance(reg, str):
            raise TypeError('bad operand type for reg')
        #if reg == '0':
        #    raise ValueError('x0 can not be set')
        x_reg = 'x'+reg
        if x_reg in self.regfiles.keys():
            return int(self.regfiles[x_reg], 2)
        else:
            raise ValueError('reg number is out of range')

    def return_all_reg (self):
        return self.regfiles


class memory(object):

    def __init__(self):
        self.mem_data = {}

    def set_mem_values(self, addr, values):
        # addr/values input are str and int respectively,such as ('320', 666)
        if not isinstance(addr, str):
            raise TypeError('bad operand type for addr')
        if not isinstance(values, int):
            raise TypeError('bad operand type for values')
        addr_int = int(addr, 10)
        values = str(intToBin(values, 32))
        if addr_int % 4 != 0:
            raise ValueError('addr is not word aligned')
        self.mem_data[addr] = values

    def get_mem_values(self, addr):
        # addr/values input are both str,such as ('320','FFFFFFFF')
        if not isinstance(addr, str):
            raise TypeError('bad operand type for addr')
        addr_int = int(addr, 10)
        if addr_int % 4 != 0:
            raise ValueError('addr is not word aligned')
        return int(self.mem_data[addr], 2)

    def return_mem (self):
        return self.mem_data


class risc_emulator(object):
    def __init__(self):
        self.regfile = regfile()
        self.memory = memory()
        self.inst_list = []
        self.pc = 0
        self.R_type = bitarray('0110011')
        self.I_type = bitarray('0010011')
        self.B_type = bitarray('1100011')
        self.S_type = bitarray('0100011')
        self.LW_type = bitarray('0000011')
        self.J_type = bitarray('1101111')

    def binToInt(self, s, num):
        # s is the binary string, and num is the number of bits
        return int(s[1:], 2) - int(s[0]) * (1 << (num-1))

    def intToBin(self, i, num):
        # i is a int format number
        return (bin(((1 << num) - 1) & i)[2:]).zfill(num)

    def get_insts(self):
        with open(path + filename, 'r') as reader:
            for line in reader.readlines():
                line = line.strip()
                inst_32 = bin(int(line, 16)).replace('0b','').zfill(32)
                self.inst_list.append(inst_32)

    def bitarray2str(self, bit_str):
        if not isinstance(bit_str, (bitarray)):
            raise TypeError('bad operand type')
        bit_list = re.findall(r'\d+', str(bit_str), re.M | re.S)
        return bit_list[0]

    def str2int(self, oprand):
        if not isinstance(oprand, (str)):
            raise TypeError('bad operand type')
        return str(int(oprand, 2))

    def parse_inst(self, inst):
        if not isinstance(inst, str):
            raise TypeError('bad operand type for instruction')
        inst_b = bitarray(inst)
        if inst_b[25:32] == self.R_type:
            self.parse_inst_R(inst_b)
        elif inst_b[25:32] == self.I_type:
            self.parse_inst_I(inst_b)
        elif inst_b[25:32] == self.B_type:
            self.parse_inst_B(inst_b)
        elif inst_b[25:32] == self.J_type:
            self.parse_inst_J(inst_b)
        elif inst_b[25:32] == self.S_type:
            self.parse_inst_S(inst_b)
        elif inst_b[25:32] == self.LW_type:
            self.parse_inst_LW(inst_b)
        else:
            raise ValueError('inst is not included in insts set')

    def parse_inst_R(self, inst):
        if not isinstance(inst, bitarray):
            raise TypeError('bad operand type for instruction')
        rs2 = str(self.str2int(self.bitarray2str(inst[7:12])))
        rs1 = str(self.str2int(self.bitarray2str(inst[12:17])))
        rd = str(self.str2int(self.bitarray2str(inst[20:25])))
        rs1_value = self.regfile.get_reg_values(rs1)
        rs2_value = self.regfile.get_reg_values(rs2)

        #add op
        if inst[0:7] == bitarray('0000000') and inst[17:20] == bitarray('000'):
            rd_value = rs1_value + rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        #sub op
        elif inst[0:7] == bitarray('0100000') and inst[17:20] == bitarray('000'):
            rd_value = rs1_value - rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        #and op
        elif inst[0:7] == bitarray('0000000') and inst[17:20] == bitarray('111'):
            rd_value = rs1_value & rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        #or op
        elif inst[0:7] == bitarray('0000000') and inst[17:20] == bitarray('110'):
            rd_value = rs1_value | rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        #xor op
        elif inst[0:7] == bitarray('0000000') and inst[17:20] == bitarray('100'):
            rd_value = rs1_value ^ rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        # sll op
        elif inst[0:7] == bitarray('0000000') and inst[17:20] == bitarray('001'):
            rd_value = rs1_value << rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        # srl op
        elif inst[0:7] == bitarray('0000000') and inst[17:20] == bitarray('101'):
            rd_value = rs1_value >> rs2_value
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        else:
            raise ValueError('inst is not included in insts set')

    def parse_inst_I(self, inst):
        if not isinstance(inst, bitarray):
            raise TypeError('bad operand type for instruction')
        imm_data = self.binToInt(self.bitarray2str(inst[0:12]), 12)
        rs1 = str(self.str2int(self.bitarray2str(inst[12:17])))
        rs1_value = self.regfile.get_reg_values(rs1)
        rd = str(self.str2int(self.bitarray2str(inst[20:25])))
        #addi op
        if inst[17:20] == bitarray('000'):
            rd_value = rs1_value + imm_data
            self.regfile.set_reg_values(rd, rd_value)
            self.pc += 4
        else:
            raise ValueError('inst is not included in insts set')

    def parse_inst_B(self, inst):
        if not isinstance(inst, bitarray):
            raise TypeError('bad operand type for instruction')
        imm_index = bitarray()
        imm_index.append(inst[0])
        imm_index.append(inst[24])
        imm_index.extend(inst[1:7])
        imm_index.extend(inst[20:24])
        imm_index.extend('0') # imm left shift by one
        rs2 = str(self.str2int(self.bitarray2str(inst[7:12])))
        rs1 = str(self.str2int(self.bitarray2str(inst[12:17])))
        rs1_value = self.regfile.get_reg_values(rs1)
        rs2_value = self.regfile.get_reg_values(rs2)
        imm_data = self.binToInt(self.bitarray2str(imm_index), 13)
        #beq op
        if inst[17:20] == bitarray('000'):
            if rs1_value == rs2_value:
                self.pc += imm_data
            else:
                self.pc += 4
        #blt op
        elif inst[17:20] == bitarray('100'):
            if rs1_value < rs2_value:
                self.pc += imm_data
            else:
                self.pc += 4
        else:
            raise ValueError('inst is not included in insts set')

    def parse_inst_J(self, inst):
        if not isinstance(inst, bitarray):
            raise TypeError('bad operand type for instruction')
        rd = str(self.str2int(self.bitarray2str(inst[20:25])))
        imm_index = bitarray()
        imm_index.append(inst[0])
        imm_index.extend(inst[12:20])
        imm_index.extend(inst[11])
        imm_index.extend(inst[1:11])
        imm_index.extend('0') # imm left shift by one
        imm_data = self.binToInt(self.bitarray2str(imm_index), 21)
        #jal op (jump and link)
        self.regfile.set_reg_values(rd, self.pc + 4)
        self.pc += imm_data

    def parse_inst_S(self, inst):
        if not isinstance(inst, bitarray):
            raise TypeError('bad operand type for instruction')
        rs2 = str(self.str2int(self.bitarray2str(inst[7:12])))
        rs1 = str(self.str2int(self.bitarray2str(inst[12:17])))
        rs2_value = self.regfile.get_reg_values(rs2)
        rs1_value = self.regfile.get_reg_values(rs1)
        imm_index = bitarray()
        imm_index.extend(inst[0:7])
        imm_index.extend(inst[20:25])
        imm_data = self.binToInt(self.bitarray2str(imm_index), 12)
        # sw op
        if inst[17:20] == bitarray('010'):
            addr_wr = str(rs1_value + imm_data)
            data_wr = rs2_value
            self.memory.set_mem_values(addr_wr, data_wr)
            self.pc += 4
        else:
            raise ValueError('inst is not included in insts set')

    def parse_inst_LW(self, inst):
        if not isinstance(inst, bitarray):
            raise TypeError('bad operand type for instruction')
        rs1 = str(self.str2int(self.bitarray2str(inst[12:17])))
        rs1_value = self.regfile.get_reg_values(rs1)
        rd = str(self.str2int(self.bitarray2str(inst[20:25])))
        imm_index = bitarray()
        imm_index.extend(inst[0:12])
        imm_data = self.binToInt(self.bitarray2str(imm_index), 12)
        # lw op
        if inst[17:20] == bitarray('010'):
            addr_rd = str(rs1_value + imm_data)
            data_rd = self.memory.get_mem_values(addr_rd)
            self.regfile.set_reg_values(rd, data_rd)
            self.pc += 4
        else:
            raise ValueError('inst is not included in insts set')

    def get_pc(self):
        return self.pc

    def write_reg(self):
        regfile_out = self.regfile.return_all_reg()
        with open(path + outfile_reg, 'a+') as f:
            for reg, value in regfile_out.items():
                item_line = str(reg) + " : " + str(value) + '\n'
                f.write(item_line)

    def write_mem(self):
        mem_out = self.memory.return_mem()
        with open(path + outfile_mem, 'a+') as f:
            for mem, value in mem_out.items():
                item_line = str(mem) + " : " + str(value) + '\n'
                f.write(item_line)


if __name__ == '__main__':
    my_riscv = risc_emulator()
    pc = my_riscv.get_pc()
    my_riscv.get_insts()
    inst_list = my_riscv.inst_list
    while pc <= (len(inst_list) - 1) * 4:
        inst_todo = inst_list[pc//4]
        my_riscv.parse_inst(inst_todo)
        pc = my_riscv.get_pc()
    my_riscv.write_mem()
    my_riscv.write_reg()
    print('bravo! all tests have been finished!!!')





































