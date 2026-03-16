# -*- coding: utf-8 -*-
"""
Парсер для HackLang
"""

from .ast import *

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def error(self, msg):
        if self.current_token:
            raise ParseError(f"Ошибка парсера в строке {self.current_token.line}: {msg}")
        raise ParseError(f"Ошибка парсера: {msg}")

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek_type(self):
        return self.current_token.type if self.current_token else 'EOF'

    def expect(self, *types):
        if self.current_token is None:
            self.error(f"Ожидалось {types}, но достигнут конец файла")
        if self.current_token.type not in types:
            self.error(f"Ожидалось {types}, получено '{self.current_token.type}'")
        val = self.current_token.value
        self.advance()
        return val

    def parse_program(self):
        prog = Program()
        while self.current_token and self.current_token.type != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                prog.statements.append(stmt)
        return prog

    def parse_statement(self):
        tok = self.current_token
        if not tok:
            return None
        if tok.type == 'FUNCTION':
            return self.parse_function_def()
        elif tok.type == 'LET':
            return self.parse_let()
        elif tok.type == 'IF':
            return self.parse_if()
        elif tok.type == 'WHILE':
            return self.parse_while()
        elif tok.type == 'FOR':
            return self.parse_for()
        elif tok.type == 'RETURN':
            return self.parse_return()
        elif tok.type == 'IMPORT':
            return self.parse_import()
        elif tok.type == 'LBRACE':
            return self.parse_block()
        else:
            expr = self.parse_expression()
            self.expect('SEMICOLON')
            return ExprStmt(expr)

    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while self.current_token and self.current_token.type != 'RBRACE':
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        self.expect('RBRACE')
        return stmts

    def parse_function_def(self):
        self.expect('FUNCTION')
        name = self.expect('IDENT')
        self.expect('LPAREN')
        params = []
        if self.current_token and self.current_token.type != 'RPAREN':
            params.append(self.expect('IDENT'))
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                params.append(self.expect('IDENT'))
        self.expect('RPAREN')
        body = self.parse_block()
        return FunctionDef(name, params, body)

    def parse_import(self):
        self.expect('IMPORT')
        filename = self.expect('STRING')
        self.expect('SEMICOLON')
        # сохраним как специальный узел, но выполнять будем позже
        from .ast import Literal
        return ExprStmt(Call(Identifier('__import__'), [Literal(filename)]))

    def parse_let(self):
        self.expect('LET')
        mutable = False
        if self.current_token and self.current_token.type == 'MUT':
            mutable = True
            self.advance()
        name = self.expect('IDENT')
        expr = None
        if self.current_token and self.current_token.type == 'ASSIGN':
            self.advance()
            expr = self.parse_expression()
        self.expect('SEMICOLON')
        return LetStmt(name, expr, mutable)

    def parse_if(self):
        self.expect('IF')
        condition = self.parse_expression()
        then_branch = self.parse_block()
        else_branch = None
        if self.current_token and self.current_token.type == 'ELSE':
            self.advance()
            if self.current_token and self.current_token.type == 'IF':
                else_branch = [self.parse_if()]
            else:
                else_branch = self.parse_block()
        return IfStmt(condition, then_branch, else_branch)

    def parse_while(self):
        self.expect('WHILE')
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileStmt(condition, body)

    def parse_for(self):
        self.expect('FOR')
        var = self.expect('IDENT')
        self.expect('IN')
        start = self.parse_expression()
        self.expect('DOTDOT')
        end = self.parse_expression()
        body = self.parse_block()
        return ForStmt(var, start, end, body)

    def parse_return(self):
        self.expect('RETURN')
        expr = None
        if self.current_token and self.current_token.type != 'SEMICOLON':
            expr = self.parse_expression()
        self.expect('SEMICOLON')
        return ReturnStmt(expr)

    # Приоритеты операторов
    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()
        if self.current_token and self.current_token.type == 'ASSIGN':
            if not isinstance(left, Identifier):
                self.error("Левая часть присваивания должна быть идентификатором")
            self.advance()
            right = self.parse_expression()
            return AssignExpr(left.name, right)
        return left

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.current_token and self.current_token.type == 'OR':
            op = self.current_token.type
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(left, op, right)
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        while self.current_token and self.current_token.type == 'AND':
            op = self.current_token.type
            self.advance()
            right = self.parse_equality()
            left = BinaryOp(left, op, right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.current_token and self.current_token.type in ('EQ', 'NE'):
            op = self.current_token.type
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_addition()
        while self.current_token and self.current_token.type in ('LT', 'LE', 'GT', 'GE'):
            op = self.current_token.type
            self.advance()
            right = self.parse_addition()
            left = BinaryOp(left, op, right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(left, op, right)
        return left

    def parse_multiplication(self):
        left = self.parse_unary()
        while self.current_token and self.current_token.type in ('STAR', 'SLASH', 'PERCENT'):
            op = self.current_token.type
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left

    def parse_unary(self):
        if self.current_token and self.current_token.type in ('MINUS', 'NOT'):
            op = self.current_token.type
            self.advance()
            expr = self.parse_unary()
            return UnaryOp(op, expr)
        return self.parse_call()

    def parse_call(self):
        expr = self.parse_primary()
        while self.current_token and self.current_token.type == 'LPAREN':
            self.advance()
            args = []
            if self.current_token and self.current_token.type != 'RPAREN':
                args.append(self.parse_expression())
                while self.current_token and self.current_token.type == 'COMMA':
                    self.advance()
                    args.append(self.parse_expression())
            self.expect('RPAREN')
            expr = Call(expr, args)
        while self.current_token and self.current_token.type == 'LBRACKET':
            self.advance()
            index = self.parse_expression()
            self.expect('RBRACKET')
            expr = IndexExpr(expr, index)
        return expr

    def parse_primary(self):
        tok = self.current_token
        if not tok:
            self.error("Неожиданный конец выражения")
        if tok.type == 'NUMBER':
            self.advance()
            return Literal(tok.value)
        if tok.type == 'STRING':
            self.advance()
            return Literal(tok.value)
        if tok.type == 'TRUE':
            self.advance()
            return Literal(True)
        if tok.type == 'FALSE':
            self.advance()
            return Literal(False)
        if tok.type == 'IDENT':
            self.advance()
            return Identifier(tok.value)
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        if tok.type == 'LBRACKET':
            self.advance()
            elements = []
            if self.current_token and self.current_token.type != 'RBRACKET':
                elements.append(self.parse_expression())
                while self.current_token and self.current_token.type == 'COMMA':
                    self.advance()
                    elements.append(self.parse_expression())
            self.expect('RBRACKET')
            return ArrayLiteral(elements)
        self.error(f"Неожиданный токен: {tok.type}")