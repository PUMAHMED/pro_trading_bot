import os
from pathlib import Path

replacements = {
    '"': '"',
    '"': '"',
    '''''''''''''"': '"',
}

fixed_count = 0

for py_file in Path('.').rglob('*.py'):
    if any(part.startswith('.') or part in ['venv', 'env', '__pycache__'] 
           for part in py_file.parts):
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        original = content
        
        for wrong, correct in replacements.items():
            content = content.replace(wrong, correct)
        
        if content != original:
            py_file.write_text(content, encoding='utf-8')
            print(f"Düzeltildi: {py_file}")
            fixed_count += 1
    except Exception as e:
        print(f"Hata: {py_file} - {e}")

print(f"\nToplam {fixed_count} dosya düzeltildi.")
