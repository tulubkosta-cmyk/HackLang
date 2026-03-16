# -*- coding: utf-8 -*-
"""
Лексер для HackLang
"""

import re

class Token:
    def __init__(self, type, value=None, line=0, col=0):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

class Lexer:
    keywords = {
        'fn': 'FUNCTION',
        'let': 'LET',
        'mut': 'MUT',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'in': 'IN',
        'return': 'RETURN',
        'import': 'IMPORT',
        'true': 'TRUE',
        'false': 'FALSE',
    }

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def error(self, msg):
        raise SyntaxError(f"Лексер: {msg} в строке {self.line}, позиция {self.col}")

    def peek(self):
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def next_char(self):
        if self.pos >= len(self.source):
            return None
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace(self):
        while True:
            ch = self.peek()
            if ch is None:
                break
            if ch in ' \t\r':
                self.next_char()
            elif ch == '#':
                while True:
                    ch = self.peek()
                    if ch is None or ch == '\n':
                        break
                    self.next_char()
            else:
                break

    def read_number(self):
        start = self.pos
        dot_seen = False
        while True:
            ch = self.peek()
            if ch is None:
                break
            if ch.isdigit():
                self.next_char()
            elif ch == '.' and not dot_seen:
                dot_seen = True
                self.next_char()
            else:
                break
        num_str = self.source[start:self.pos]
        if dot_seen:
            return float(num_str)
        else:
            return int(num_str)

    def read_string(self, quote):
        start = self.pos
        escaped = False
        while True:
            ch = self.next_char()
            if ch is None:
                self.error("Незакрытая строка")
            if not escaped and ch == '\\':
                escaped = True
                continue
            if not escaped and ch == quote:
                break
            escaped = False
        return self.source[start:self.pos-1]

    def read_identifier(self):
        start = self.pos
        while True:
            ch = self.peek()
            if ch is None:
                break
            if ch.isalnum() or ch == '_':
                self.next_char()
            else:
                break
        return self.source[start:self.pos]

    def tokenize(self):
        while True:
            self.skip_whitespace()
            ch = self.peek()
            if ch is None:
                break

            # числа
            if ch.isdigit() or (ch == '-' and self.pos+1 < len(self.source) and self.source[self.pos+1].isdigit()):
                if ch == '-':
                    self.next_char()
                num = self.read_number()
                if ch == '-':
                    num = -num
                self.tokens.append(Token('NUMBER', num, self.line, self.col))
                continue

            # строки
            if ch in '"\'':
                quote = ch
                self.next_char()
                s = self.read_string(quote)
                self.tokens.append(Token('STRING', s, self.line, self.col))
                continue

            # идентификаторы и ключевые слова
            if ch.isalpha() or ch == '_':
                ident = self.read_identifier()
                tok_type = Lexer.keywords.get(ident, 'IDENT')
                self.tokens.append(Token(tok_type, ident, self.line, self.col))
                continue

            # операторы и пунктуация
            ops = {
                '+': 'PLUS', '-': 'MINUS', '*': 'STAR', '/': 'SLASH', '%': 'PERCENT',
                '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE',
                '[': 'LBRACKET', ']': 'RBRACKET', ',': 'COMMA', ';': 'SEMICOLON',
                ':': 'COLON',
            }
            if ch in ops:
                self.next_char()
                self.tokens.append(Token(ops[ch], line=self.line, col=self.col))
                continue

            if ch == '=':
                self.next_char()
                if self.peek() == '=':
                    self.next_char()
                    self.tokens.append(Token('EQ', line=self.line, col=self.col))
                else:
                    self.tokens.append(Token('ASSIGN', line=self.line, col=self.col))
                continue

            if ch == '!':
                self.next_char()
                if self.peek() == '=':
                    self.next_char()
                    self.tokens.append(Token('NE', line=self.line, col=self.col))
                else:
                    self.tokens.append(Token('NOT', line=self.line, col=self.col))
                continue

            if ch == '<':
                self.next_char()
                if self.peek() == '=':
                    self.next_char()
                    self.tokens.append(Token('LE', line=self.line, col=self.col))
                else:
                    self.tokens.append(Token('LT', line=self.line, col=self.col))
                continue

            if ch == '>':
                self.next_char()
                if self.peek() == '=':
                    self.next_char()
                    self.tokens.append(Token('GE', line=self.line, col=self.col))
                else:
                    self.tokens.append(Token('GT', line=self.line, col=self.col))
                continue

            if ch == '&':
                self.next_char()
                if self.peek() == '&':
                    self.next_char()
                    self.tokens.append(Token('AND', line=self.line, col=self.col))
                else:
                    self.error("Ожидалось '&&'")
                continue

            if ch == '|':
                self.next_char()
                if self.peek() == '|':
                    self.next_char()
                    self.tokens.append(Token('OR', line=self.line, col=self.col))
                else:
                    self.error("Ожидалось '||'")
                continue

            if ch == '.':
                self.next_char()
                if self.peek() == '.':
                    self.next_char()
                    self.tokens.append(Token('DOTDOT', line=self.line, col=self.col))
                else:
                    self.tokens.append(Token('DOT', line=self.line, col=self.col))
                continue

            self.error(f"Неожиданный символ '{ch}'")

        return self.tokens