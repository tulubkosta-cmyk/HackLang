# -*- coding: utf-8 -*-
"""
Интерпретатор HackLang
"""

from .ast import *
import sys

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class HackLangRuntime:
    def __init__(self, lib_path=None):
        self.globals = {}
        self.functions = {}
        self.builtins = {}
        self.proxy = None
        self.proxy_handler = None
        self.lib_path = lib_path or os.path.join(os.path.expanduser("~"), ".hacklang", "lib")
        self._setup_builtins()

    def _setup_builtins(self):
        # Будут заполнены извне через register_builtin
        pass

    def register_builtin(self, name, func):
        self.builtins[name] = func

    def set_proxy(self, proxy_string):
        import urllib.request
        self.proxy = proxy_string
        self.proxy_handler = urllib.request.ProxyHandler({
            'http': proxy_string,
            'https': proxy_string,
        })

    def clear_proxy(self):
        self.proxy = None
        self.proxy_handler = None

    def run(self, program):
        try:
            self.execute_block(program.statements, self.globals)
        except ReturnException:
            pass

    def execute_block(self, stmts, env):
        local_env = env.copy()
        for stmt in stmts:
            self.execute_stmt(stmt, local_env)

    def execute_stmt(self, stmt, env):
        if isinstance(stmt, FunctionDef):
            self.functions[stmt.name] = stmt
        elif isinstance(stmt, LetStmt):
            value = None
            if stmt.expr:
                value = self.eval_expr(stmt.expr, env)
            env[stmt.name] = value
        elif isinstance(stmt, IfStmt):
            cond = self.eval_expr(stmt.condition, env)
            if self.is_truthy(cond):
                self.execute_block(stmt.then_branch, env)
            elif stmt.else_branch:
                self.execute_block(stmt.else_branch, env)
        elif isinstance(stmt, WhileStmt):
            while True:
                cond = self.eval_expr(stmt.condition, env)
                if not self.is_truthy(cond):
                    break
                self.execute_block(stmt.body, env)
        elif isinstance(stmt, ForStmt):
            start = self.eval_expr(stmt.start, env)
            end = self.eval_expr(stmt.end, env)
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                raise RuntimeError("Границы цикла for должны быть числами")
            for_env = env.copy()
            i = int(start)
            while i < int(end):
                for_env[stmt.var] = i
                self.execute_block(stmt.body, for_env)
                i += 1
        elif isinstance(stmt, ReturnStmt):
            value = None
            if stmt.expr:
                value = self.eval_expr(stmt.expr, env)
            raise ReturnException(value)
        elif isinstance(stmt, ExprStmt):
            self.eval_expr(stmt.expr, env)
        else:
            raise RuntimeError(f"Неизвестный оператор: {type(stmt)}")

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Identifier):
            if expr.name in env:
                return env[expr.name]
            if expr.name in self.builtins:
                return self.builtins[expr.name]
            raise RuntimeError(f"Неизвестная переменная: {expr.name}")
        if isinstance(expr, BinaryOp):
            left = self.eval_expr(expr.left, env)
            right = self.eval_expr(expr.right, env)
            if expr.op == 'PLUS':
                return left + right
            if expr.op == 'MINUS':
                return left - right
            if expr.op == 'STAR':
                return left * right
            if expr.op == 'SLASH':
                return left / right
            if expr.op == 'PERCENT':
                return left % right
            if expr.op == 'EQ':
                return left == right
            if expr.op == 'NE':
                return left != right
            if expr.op == 'LT':
                return left < right
            if expr.op == 'LE':
                return left <= right
            if expr.op == 'GT':
                return left > right
            if expr.op == 'GE':
                return left >= right
            if expr.op == 'AND':
                return self.is_truthy(left) and self.is_truthy(right)
            if expr.op == 'OR':
                return self.is_truthy(left) or self.is_truthy(right)
            raise RuntimeError(f"Неизвестный оператор: {expr.op}")
        if isinstance(expr, UnaryOp):
            val = self.eval_expr(expr.expr, env)
            if expr.op == 'MINUS':
                return -val
            if expr.op == 'NOT':
                return not self.is_truthy(val)
            raise RuntimeError(f"Неизвестный унарный оператор: {expr.op}")
        if isinstance(expr, Call):
            callee = self.eval_expr(expr.func, env)
            args = [self.eval_expr(arg, env) for arg in expr.args]
            if callable(callee):
                return callee(*args)
            if isinstance(callee, FunctionDef):
                if len(args) != len(callee.params):
                    raise RuntimeError(f"Функция {callee.name} ожидает {len(callee.params)} аргументов, получено {len(args)}")
                func_env = {}
                for param, arg in zip(callee.params, args):
                    func_env[param] = arg
                try:
                    self.execute_block(callee.body, func_env)
                except ReturnException as ret:
                    return ret.value
                return None
            raise RuntimeError(f"Попытка вызвать не-функцию: {callee}")
        if isinstance(expr, IndexExpr):
            obj = self.eval_expr(expr.obj, env)
            idx = self.eval_expr(expr.index, env)
            if isinstance(obj, (list, str, dict)):
                if isinstance(obj, dict):
                    return obj.get(idx, None)
                if not isinstance(idx, int):
                    raise RuntimeError("Индекс должен быть целым числом")
                if idx < 0 or idx >= len(obj):
                    raise RuntimeError("Индекс вне границ")
                return obj[idx]
            raise RuntimeError(f"Индексация не поддерживается для {type(obj)}")
        if isinstance(expr, AssignExpr):
            if expr.name not in env:
                raise RuntimeError(f"Переменная '{expr.name}' не определена")
            value = self.eval_expr(expr.value, env)
            env[expr.name] = value
            return value
        if isinstance(expr, ArrayLiteral):
            return [self.eval_expr(e, env) for e in expr.elements]
        raise RuntimeError(f"Неизвестное выражение: {type(expr)}")

    def is_truthy(self, val):
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, (str, list, dict)):
            return len(val) > 0
        return True