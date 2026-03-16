# -*- coding: utf-8 -*-
"""
Виртуальная машина HackLang (стековая)
"""

class VM:
    def __init__(self):
        self.stack = []
        self.vars = {}
        self.ip = 0  # instruction pointer
        self.code = []

    def load(self, bytecode):
        self.code = bytecode
        self.ip = 0

    def run(self):
        while self.ip < len(self.code):
            instr = self.code[self.ip]
            self.ip += 1
            self.execute(instr)

    def execute(self, instr):
        op = instr[0]
        if op == 'PUSH':
            self.stack.append(instr[1])
        elif op == 'POP':
            self.stack.pop()
        elif op == 'STORE':
            name = instr[1]
            self.vars[name] = self.stack.pop()
        elif op == 'LOAD':
            name = instr[1]
            self.stack.append(self.vars[name])
        elif op == 'ADD':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif op == 'SUB':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        elif op == 'MUL':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        elif op == 'DIV':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a / b)
        elif op == 'PRINT':
            val = self.stack.pop()
            print(val)
        elif op == 'HALT':
            self.ip = len(self.code)  # останов
        else:
            raise RuntimeError(f"Unknown opcode: {op}")