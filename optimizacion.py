import ast
import operator as op
import re

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.floordiv,
}

known_pure_functions = {
    'fac': lambda n: 1 if n < 2 else known_pure_functions['fac'](n - 1) * n,
    'abs': lambda n: n if n >= 0 else -n,
    # Puedes agregar más funciones puras aquí
}

def eval_expr(expr):
    # Evalúa una expresión constante usando AST (para safe evaluation)
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Num):  # Números
            return node.n
        elif isinstance(node, ast.BinOp):  # Operaciones binarias
            left = _eval(node.left)
            right = _eval(node.right)
            if type(node.op) in operators:
                return operators[type(node.op)](left, right)
            else:
                raise TypeError(f"Operador no soportado: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):  # Negativos, etc.
            return -_eval(node.operand)
        elif isinstance(node, ast.Call):  # Llamada a función
            func_name = node.func.id
            args = [_eval(arg) for arg in node.args]
            if func_name in known_pure_functions and all(isinstance(a, (int, float)) for a in args):
                return known_pure_functions[func_name](*args)
            else:
                raise ValueError("Función desconocida o argumentos no constantes")
        else:
            raise TypeError(f"Nodo desconocido: {type(node)}")

    try:
        node = ast.parse(expr.strip(), mode='eval')
        return _eval(node)
    except Exception:
        return None  

def apply_constant_folding(line):
    """
    Busca cualquier expresión evaluable como constante y la reemplaza por su valor.
    Incluye llamadas a funciones puras con parámetros constantes.
    """
    new_line = list(line)

    # Detecta patrones como: = 10 + 5 * 3 + 30 o == 1*4+10
    pattern = r'([=+\-*/<>=!]+)\s*([^;()\n]+)'
    matches = re.finditer(pattern, line)

    for match in reversed(list(matches)):
        expr = match.group(2).strip()
        result = eval_expr(expr)
        if result is not None:
            start = match.start(2)
            end = match.end(2)
            new_line[start:end] = str(result)

    return ''.join(new_line)

def optimize_code(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    optimized_lines = []
    in_main_function = False
    in_while_loop = False
    hoisted_code_block = []
    hoisted_vars = set()
    function_stack = []

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Inicio de función
        if stripped_line.startswith("fun") and "main()" in stripped_line:
            in_main_function = True
            optimized_lines.append(line)
            continue

        # Fin de función
        if stripped_line == "endfun":
            if in_main_function:
                # Insertar código hoisteado al inicio del main, después de las declaraciones
                insert_idx = len(optimized_lines)
                for k in range(len(optimized_lines)):
                    if "var int" in optimized_lines[k]:
                        insert_idx = k + 1
                if hoisted_code_block:
                    optimized_lines[insert_idx:insert_idx] = [f"{l}\n" for l in hoisted_code_block]

            in_main_function = False
            in_while_loop = False
            optimized_lines.append(line)
            continue

        # Inicio de bucle while
        if "while" in stripped_line and "do" in stripped_line:
            in_while_loop = True
            optimized_lines.append(line)
            continue

        # Fin de bucle while
        if stripped_line == "endwhile;":
            in_while_loop = False
            optimized_lines.append(line)
            continue

        # Procesar líneas dentro del while
        if in_while_loop and '=' in stripped_line:
            var_name = stripped_line.split('=')[0].strip()
            expr = '='.join(stripped_line.split('=')[1:]).strip().rstrip(';')

            # Verificar si la expresión es constante
            result = eval_expr(expr)
            if result is not None and var_name not in hoisted_vars:
                indent = line[:line.find(line.lstrip())]
                hoisted_code_block.append(f"{indent}{var_name} = {result};")
                hoisted_vars.add(var_name)
                continue  # Omitir línea original dentro del bucle

        # Aplicar constant folding a cualquier línea
        processed_line = apply_constant_folding(line)
        optimized_lines.append(processed_line)

    # Escribir salida
    with open(output_file, 'w') as outfile:
        outfile.writelines(optimized_lines)
"""
# Archivos de prueba
inputs = [
    ('input1.txt', 'input1_optimized.txt'),
    ('input2.txt', 'input2_optimized.txt'),
    ('input3.txt', 'input3_optimized.txt'),
    ('input4.txt', 'input4_optimized.txt'),
]

for input_name, output_name in inputs:
    input_path = f'./inputs/{input_name}'
    output_path = f'./inputs/{output_name}'
    optimize_code(input_path, output_path)
    print(f"\n--- Contenido optimizado: {output_name} ---")
    with open(output_path, 'r') as f:
        print(f.read())
"""