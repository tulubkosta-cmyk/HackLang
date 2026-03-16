# -*- coding: utf-8 -*-
"""
H.A.L. – HackLang Autonomous Guardian
Анализирует код, ищет потенциальные проблемы, выдаёт рекомендации
"""

import re

class HAL:
    def __init__(self):
        self.issues = []
        self.stats = {
            'lines_analyzed': 0,
            'errors_found': 0,
            'warnings_given': 0,
        }

    def analyze(self, source_code):
        self.issues = []
        lines = source_code.split('\n')
        self.stats['lines_analyzed'] += len(lines)

        # Поиск подозрительных паттернов
        for i, line in enumerate(lines, 1):
            # Бесконечный цикл while True без break
            if 'while True' in line and 'break' not in source_code[i:]:
                self.issues.append({
                    'line': i,
                    'type': 'warning',
                    'message': 'Возможен бесконечный цикл: while True без break'
                })

            # Присваивание вместо сравнения в условии
            if 'if ' in line and '=' in line and '==' not in line and '!=' not in line:
                self.issues.append({
                    'line': i,
                    'type': 'warning',
                    'message': 'В условии if возможно присваивание (=), а не сравнение (==)'
                })

            # Неиспользуемые переменные (очень примитивно)
            if 'let ' in line:
                var_name = line.split('let')[1].split('=')[0].strip()
                if var_name and var_name not in source_code[i:]:
                    self.issues.append({
                        'line': i,
                        'type': 'info',
                        'message': f'Переменная "{var_name}" объявлена, но не используется'
                    })

            # Проверка на опасные функции (system)
            if 'system(' in line:
                self.issues.append({
                    'line': i,
                    'type': 'warning',
                    'message': 'Использование system() может быть опасно, убедитесь в безопасности аргументов'
                })

            # Деление на ноль
            if '/ 0' in line or '/0' in line:
                self.issues.append({
                    'line': i,
                    'type': 'error',
                    'message': 'Обнаружено деление на ноль'
                })

        self.stats['errors_found'] += len([x for x in self.issues if x['type'] == 'error'])
        self.stats['warnings_given'] += len([x for x in self.issues if x['type'] == 'warning'])
        return self.issues

    def print_report(self, color=True):
        if not self.issues:
            if color:
                print("\033[92m[H.A.L.] Код чист, проблем не обнаружено.\033[0m")
            else:
                print("[H.A.L.] Код чист, проблем не обнаружено.")
        else:
            if color:
                print("\033[93m[H.A.L.] Найдены потенциальные проблемы:\033[0m")
            else:
                print("[H.A.L.] Найдены потенциальные проблемы:")
            for issue in self.issues:
                if color:
                    if issue['type'] == 'error':
                        color_code = '\033[91m'
                    elif issue['type'] == 'warning':
                        color_code = '\033[93m'
                    else:
                        color_code = '\033[96m'
                    print(f"{color_code}  строка {issue['line']}: {issue['message']}\033[0m")
                else:
                    print(f"  строка {issue['line']}: {issue['message']}")

    def status(self):
        return self.stats