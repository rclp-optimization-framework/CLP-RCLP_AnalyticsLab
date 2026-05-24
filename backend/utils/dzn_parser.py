"""
Parser para convertir archivos DZN (MiniZinc Data) a formato JSON/dict.
El formato DZN puede contener:
- Asignaciones simples: variable = valor;
- Arrays: array_var = [val1, val2, ...];
- Arrays 2D: array2d(1..n, 1..m, [values]);
"""

import re
from typing import Any, Dict


def parse_dzn_line(line: str) -> tuple[str, Any] | None:
    """
    Parsea una línea individual de DZN.
    Retorna (nombre_variable, valor) o None si no es válida.
    """
    # Remover comentarios
    line = re.sub(r'%.*$', '', line).strip()
    if not line or line.startswith('%'):
        return None

    # Patrón: variable_name = value;
    match = re.match(r'(\w+)\s*=\s*(.+?);', line)
    if not match:
        return None

    name = match.group(1)
    value_str = match.group(2).strip()

    # Parsear el valor
    try:
        value = parse_dzn_value(value_str)
        return (name, value)
    except Exception as e:
        print(f"Warning: Could not parse '{name} = {value_str}': {e}")
        return None


def parse_dzn_value(value_str: str) -> Any:
    """
    Parsea un valor DZN que puede ser:
    - Número: 123, 12.5
    - Array: [1, 2, 3]
    - Array 2D: array2d(1..n, 1..m, [...])
    """
    value_str = value_str.strip()

    # Check for array2d
    if value_str.startswith('array2d'):
        return parse_array2d(value_str)

    # Check for simple array
    if value_str.startswith('[') and value_str.endswith(']'):
        return parse_array(value_str)

    # Try parsing as number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        # Maybe it's a string
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        raise ValueError(f"Cannot parse value: {value_str}")


def parse_array(array_str: str) -> list:
    """Parsea un array DZN: [val1, val2, val3, ...]"""
    # Remover corchetes
    inner = array_str[1:-1].strip()
    if not inner:
        return []

    # Split by comma, but be careful with nested arrays
    elements = []
    current = ''
    depth = 0

    for char in inner:
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
        elif char == ',' and depth == 0:
            if current.strip():
                elements.append(parse_dzn_value(current.strip()))
            current = ''
            continue

        current += char

    if current.strip():
        elements.append(parse_dzn_value(current.strip()))

    return elements


def parse_array2d(array2d_str: str) -> list[list]:
    """
    Parsea un array 2D: array2d(1..rows, 1..cols, [values])
    Retorna una lista de listas.
    """
    # Extraer el contenido dentro de array2d()
    match = re.match(r'array2d\s*\(\s*1\.\..+?,\s*1\.\..+?,\s*(\[.+\])\s*\)', array2d_str, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid array2d format: {array2d_str}")

    values_str = match.group(1)
    flat_values = parse_array(values_str)

    # Determinar dimensiones desde el patrón
    dim_match = re.match(r'array2d\s*\(\s*1\.\.(\d+),\s*1\.\.(\d+),', array2d_str)
    if not dim_match:
        raise ValueError(f"Cannot extract dimensions from: {array2d_str}")

    rows = int(dim_match.group(1))
    cols = int(dim_match.group(2))

    # Reorganizar flat array en matriz
    matrix = []
    for i in range(rows):
        row = flat_values[i * cols : (i + 1) * cols]
        matrix.append(row)

    return matrix


def parse_dzn_content(content: str) -> Dict[str, Any]:
    """
    Parsea el contenido completo de un archivo DZN.
    Retorna un diccionario con todos los parámetros.
    """
    result = {}
    lines = content.split('\n')

    # Procesar línea por línea
    i = 0
    while i < len(lines):
        line = lines[i]

        # Remover comentarios al inicio
        line_clean = re.sub(r'%.*$', '', line).strip()

        # Si no hay punto y coma, podría ser una línea multilinea
        if line_clean and not line_clean.endswith(';'):
            # Acumular líneas hasta encontrar punto y coma
            accumulated = line
            i += 1
            while i < len(lines) and not accumulated.strip().endswith(';'):
                accumulated += ' ' + lines[i]
                i += 1
            line = accumulated
        else:
            i += 1

        # Parsear línea
        parsed = parse_dzn_line(line)
        if parsed:
            name, value = parsed
            result[name] = value

    return result


def dzn_to_test_input(dzn_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte un diccionario DZN parseado a formato TestInput (JSON).
    Mapea nombres DZN a nombres de campos de TestInput.
    """
    mapping = {
        'num_buses': 'num_buses',
        'num_stations': 'num_stations',
        'max_stops': 'max_stops',
        'num_stops': 'num_stops',
        'st_bi': 'st_bi',
        'D': 'd',  # Energy consumption (D en DZN)
        'T': 't',  # Travel times (T en DZN)
        'tau_bi': 'tau_bi',  # Timetable
        'Cmax': 'consumo_max',  # Max consumption (Cmax = consumo_max)
        'Cmin': 'consumo_min',  # Min consumption (Cmin = consumo_min)
        'alpha': 'alpha',  # Charging rate
        'mu': 'mu',  # Max delay
        'SM': 'sm',  # Safety margin
        'psi': 'psi',  # Min charging time
        'beta': 'beta',  # Max charging time
        'M': 'm',  # Big M constant
    }

    result = {}
    for dzn_key, test_key in mapping.items():
        if dzn_key in dzn_dict:
            result[test_key] = dzn_dict[dzn_key]

    return result


def parse_dzn_file(file_path: str) -> Dict[str, Any]:
    """
    Lee un archivo DZN y retorna el diccionario parseado.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_dzn_content(content)


def parse_dzn_to_test_input(dzn_content: str) -> Dict[str, Any]:
    """
    Parsea contenido DZN y lo convierte directamente a TestInput format.
    """
    dzn_dict = parse_dzn_content(dzn_content)
    return dzn_to_test_input(dzn_dict)


if __name__ == "__main__":
    # Test parsing
    sample_dzn = """
    num_buses = 5;
    num_stations = 8;
    Cmax = 1000;
    Cmin = 200;
    alpha = 100;
    mu = 50;
    SM = 10;
    psi = 10;
    beta = 100;
    M = 10000;
    max_stops = 8;
    num_stops = [8,8,8,8,8];
    st_bi = array2d(1..5, 1..8, [
      1,2,3,4,5,6,7,8,
      8,7,6,5,4,3,2,1,
      1,3,5,7,2,4,6,8,
      2,4,6,8,1,3,5,7,
      1,4,7,2,5,8,3,6
    ]);
    """

    parsed = parse_dzn_to_test_input(sample_dzn)
    print("Parsed DZN:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
