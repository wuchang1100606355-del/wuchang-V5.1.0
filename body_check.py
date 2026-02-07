import os
import py_compile
import sys

def check_syntax(file_path):
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

print('Starting Body Check (Syntax Analysis)...')
root_dir = os.getcwd()
valid_files = []
invalid_files = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Skip excluded directories
    if 'venv' in dirpath or 'node_modules' in dirpath or 'Rollback_Points' in dirpath or 'SPACETIME_SNAPSHOTS' in dirpath:
        continue
        
    for filename in filenames:
        if filename.endswith('.py'):
            full_path = os.path.join(dirpath, filename)
            is_valid, error = check_syntax(full_path)
            if is_valid:
                valid_files.append(full_path)
            else:
                invalid_files.append((full_path, error))
                print(f'❌ [Broken Limb] {full_path}: {error}')

print(f'\nHealth Report:')
print(f'✅ Functional Limbs: {len(valid_files)}')
print(f'❌ Broken/Necrotic Limbs: {len(invalid_files)}')

# Check for old 'sister' imports in valid files
print('\nChecking for Phantom Limb Pain (Legacy Imports)...')
legacy_terms = ['core_sister_service', 'sister_ai_learning_integration', 'sister_growth_dashboard', 'sister_agent']
affected_files = []

for file_path in valid_files:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for term in legacy_terms:
                if term in content:
                    print(f'⚠️ [Phantom Pain] {file_path} references legacy term: {term}')
                    affected_files.append(file_path)
                    break
    except Exception as e:
        print(f'Could not read {file_path}: {e}')

