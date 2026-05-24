/**
 * DZN Parser for TypeScript
 * Parses MiniZinc data format (.dzn) files
 */

export function parseDznContent(content: string): Record<string, any> {
  const result: Record<string, any> = {};
  const lines = content.split("\n");

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    // Remove comments
    line = line.replace(/%.*$/, "").trim();
    if (!line) continue;

    // Handle multi-line statements
    while (line && !line.endsWith(";")) {
      i++;
      if (i >= lines.length) break;
      let nextLine = lines[i].replace(/%.*$/, "").trim();
      if (nextLine) line += " " + nextLine;
    }

    // Parse line: variable_name = value;
    const match = line.match(/(\w+)\s*=\s*(.+?);/);
    if (!match) continue;

    const name = match[1];
    const valueStr = match[2].trim();

    try {
      const value = parseDznValue(valueStr);
      result[name] = value;
    } catch (e) {
      console.warn(`Could not parse '${name} = ${valueStr}': ${e}`);
    }
  }

  return result;
}

function parseDznValue(valueStr: string): any {
  valueStr = valueStr.trim();

  // Check for array2d
  if (valueStr.startsWith("array2d")) {
    return parseArray2d(valueStr);
  }

  // Check for simple array
  if (valueStr.startsWith("[") && valueStr.endsWith("]")) {
    return parseArray(valueStr);
  }

  // Try parsing as number
  if (/^-?\d+(\.\d+)?$/.test(valueStr)) {
    return /\./.test(valueStr) ? parseFloat(valueStr) : parseInt(valueStr, 10);
  }

  // String
  if (valueStr.startsWith('"') && valueStr.endsWith('"')) {
    return valueStr.slice(1, -1);
  }

  throw new Error(`Cannot parse value: ${valueStr}`);
}

function parseArray(arrayStr: string): any[] {
  const inner = arrayStr.slice(1, -1).trim();
  if (!inner) return [];

  const elements: any[] = [];
  let current = "";
  let depth = 0;

  for (let i = 0; i < inner.length; i++) {
    const char = inner[i];

    if (char === "[") depth++;
    else if (char === "]") depth--;
    else if (char === "," && depth === 0) {
      if (current.trim()) {
        elements.push(parseDznValue(current.trim()));
      }
      current = "";
      continue;
    }

    current += char;
  }

  if (current.trim()) {
    elements.push(parseDznValue(current.trim()));
  }

  return elements;
}

function parseArray2d(array2dStr: string): number[][] {
  // Extract content within array2d()
  const match = array2dStr.match(
    /array2d\s*\(\s*1\.\.(\d+),\s*1\.\.(\d+),\s*(\[.+\])\s*\)/s,
  );
  if (!match) {
    throw new Error(`Invalid array2d format: ${array2dStr}`);
  }

  const rows = parseInt(match[1], 10);
  const cols = parseInt(match[2], 10);
  const valuesStr = match[3];

  const flatValues = parseArray(valuesStr);

  // Reshape to matrix
  const matrix: number[][] = [];
  for (let i = 0; i < rows; i++) {
    const row = flatValues.slice(i * cols, (i + 1) * cols);
    matrix.push(row);
  }

  return matrix;
}

export function dznToTestInput(
  dznDict: Record<string, any>,
): Record<string, any> {
  const mapping: Record<string, string> = {
    num_buses: "num_buses",
    num_stations: "num_stations",
    max_stops: "max_stops",
    num_stops: "num_stops",
    st_bi: "st_bi",
    D: "d",
    T: "t",
    tau_bi: "tau_bi",
    Cmax: "consumo_max",
    Cmin: "consumo_min",
    alpha: "alpha",
    mu: "mu",
    SM: "sm",
    psi: "psi",
    beta: "beta",
    M: "m",
  };

  const result: Record<string, any> = {};
  for (const [dznKey, testKey] of Object.entries(mapping)) {
    if (dznKey in dznDict) {
      result[testKey] = dznDict[dznKey];
    }
  }

  return result;
}

export async function parseDznFile(file: File): Promise<Record<string, any>> {
  const content = await file.text();
  const dznDict = parseDznContent(content);
  return dznToTestInput(dznDict);
}

export async function parseJsonFile(file: File): Promise<any> {
  const content = await file.text();
  return JSON.parse(content);
}
