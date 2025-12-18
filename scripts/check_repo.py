import ast
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_requirements(req_path: Path):
    pkgs = set()
    if not req_path.exists():
        return pkgs
    for line in req_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # extract package name before any extras or version spec
        name = line.split(';')[0].split('[')[0]
        for sep in ['==', '>=', '<=', '~=', '>', '<']:
            if sep in name:
                name = name.split(sep)[0]
        name = name.strip().lower()
        if name:
            pkgs.add(name)
    return pkgs

def gather_py_files(root: Path):
    for p in root.rglob('*.py'):
        if 'site-packages' in str(p) or 'venv' in str(p) or '__pycache__' in str(p):
            continue
        yield p

def extract_imports(source: str):
    imports = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def main():
    reqs = load_requirements(ROOT / 'requirements.txt')
    errors = []
    missing_deps = {}
    print(f"Checking Python files under: {ROOT}")
    for f in gather_py_files(ROOT):
        rel = f.relative_to(ROOT)
        src = f.read_text(encoding='utf-8')
        imports = extract_imports(src)
        if imports is None:
            errors.append((str(rel), 'SYNTAX_ERROR'))
            continue
        # filter local imports
        external = set()
        for imp in imports:
            if imp.startswith('app') or imp.startswith('.') or imp in ('typing', 'json', 'os', 're', 'sys', 'pathlib', 'csv', 'ast', 'dataclasses', 'logging', 'functools', 'itertools', 'collections', 'enum'):
                continue
            external.add(imp.lower())
        # check presence in requirements
        not_listed = [e for e in sorted(external) if not any(e == r or e.startswith(r) or r.startswith(e) for r in reqs)]
        if not_listed:
            missing_deps[str(rel)] = not_listed

    print('\nSummary:')
    if errors:
        print('Files with syntax errors:')
        for f, _ in errors:
            print(' -', f)
    else:
        print('No syntax errors found.')

    if missing_deps:
        print('\nPotential external imports not listed in requirements.txt:')
        for f, deps in missing_deps.items():
            print(f' - {f}: {', '.join(deps)}')
    else:
        print('\nAll external imports appear listed in requirements.txt (heuristic).')

if __name__ == '__main__':
    main()
