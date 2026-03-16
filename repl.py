# -*- coding: utf-8 -*-
"""
REPL для HackLang с поддержкой H.A.L. и цветами
"""

import sys
import os
from .lexer import Lexer
from .parser import Parser
from .interpreter import HackLangRuntime
from .builtins import register_all
from .hal import HAL

# Цвета
try:
    import colorama
    colorama.init()
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    RED = colorama.Fore.RED
    CYAN = colorama.Fore.CYAN
    MAGENTA = colorama.Fore.MAGENTA
    RESET = colorama.Style.RESET_ALL
except:
    GREEN = YELLOW = RED = CYAN = MAGENTA = RESET = ''

def repl(lib_path=None):
    runtime = HackLangRuntime(lib_path)
    register_all(runtime)
    hal = HAL()

    print(f"{CYAN}HackLang v0.1-dev-hal с H.A.L. (прототип){RESET}")
    print("Команды: :exit, :paste, :hal, :help")

    buffer = []
    paste_mode = False

    while True:
        try:
            if paste_mode:
                line = input(f"{YELLOW}(paste) {RESET}")
            else:
                line = input(f"{GREEN}>> {RESET}")
        except (EOFError, KeyboardInterrupt):
            if paste_mode:
                paste_mode = False
                code = '\n'.join(buffer)
                buffer = []
                if code.strip():
                    _execute_code(code, runtime, hal)
                continue
            else:
                print(f"{MAGENTA}\nПока, Костя!{RESET}")
                break

        line = line.rstrip('\n')
        if not paste_mode:
            if line == ':exit':
                break
            elif line == ':help':
                print(f"{CYAN}Доступные команды:{RESET}")
                print("  :exit  – выход")
                print("  :paste – режим многострочного ввода")
                print("  :hal   – статистика H.A.L.")
                print("  :help  – эта справка")
                continue
            elif line == ':paste':
                paste_mode = True
                buffer = []
                print(f"{YELLOW}Режим вставки. Введите код, завершите пустой строкой или Ctrl+D.{RESET}")
                continue
            elif line == ':hal':
                print(f"{CYAN}Статистика H.A.L.:{RESET} {hal.status()}")
                continue
            elif line.strip() == '':
                continue

        if paste_mode:
            if line == '' or line == ':end':
                paste_mode = False
                code = '\n'.join(buffer)
                buffer = []
                if code.strip():
                    _execute_code(code, runtime, hal)
            else:
                buffer.append(line)
        else:
            if line.strip():
                _execute_code(line, runtime, hal)

def _execute_code(code, runtime, hal):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        prog = parser.parse_program()
        runtime.run(prog)
        issues = hal.analyze(code)
        hal.print_report(color=True)
    except Exception as e:
        print(f"{RED}Ошибка: {e}{RESET}")

def run_file(filename, lib_path=None):
    runtime = HackLangRuntime(lib_path)
    register_all(runtime)
    hal = HAL()
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        prog = parser.parse_program()
        runtime.run(prog)
        issues = hal.analyze(code)
        hal.print_report(color=True)
    except Exception as e:
        print(f"{RED}Ошибка: {e}{RESET}")