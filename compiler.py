def compile_to_bytecode(self, source_code):
    # Простейший компилятор выражений
    # Пока только для присваиваний и печати
    bytecode = []
    lines = source_code.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('let '):
            # let x = 5 + 3
            expr = line[4:].strip().rstrip(';')
            if '=' in expr:
                var, val_expr = expr.split('=', 1)
                var = var.strip()
                # Парсим простое выражение (числа и +)
                tokens = val_expr.split()
                for token in tokens:
                    if token.isdigit():
                        bytecode.append(('PUSH', int(token)))
                    elif token == '+':
                        # операция ADD будет применена позже
                        pass
                # Упрощённо: кладём результат на стек и сохраняем
                bytecode.append(('STORE', var))
        elif line.startswith('print'):
            # print(x)
            arg = line[5:].strip().strip('(').rstrip(')').strip()
            if arg:
                bytecode.append(('LOAD', arg))
                bytecode.append(('PRINT',))
    bytecode.append(('HALT',))
    return bytecode