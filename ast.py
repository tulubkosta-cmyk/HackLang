# -*- coding: utf-8 -*-
"""
Абстрактное синтаксическое дерево (AST) для HackLang
"""

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self):
        self.statements = []

class LetStmt(ASTNode):
    def __init__(self, name, expr, mutable=False):
        self.name = name
        self.expr = expr
        self.mutable = mutable

class IfStmt(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStmt(ASTNode):
    def __init__(self, var, start, end, body):
        self.var = var
        self.start = start
        self.end = end
        self.body = body

class ReturnStmt(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr

class ExprStmt(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Call(ASTNode):
    def __init__(self, func, args):
        self.func = func
        self.args = args

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class ArrayLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class IndexExpr(ASTNode):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

class AssignExpr(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class DictLiteral(ASTNode):
    def __init__(self, pairs):
        self.pairs = pairs  # список кортежей (ключ, значение)