import os
import glob

# Değiştirilecek karakterler
replacements = {
    '"': '"',  # Sol tipografik tırnak
    '"': '"',  # Sağ tipografik tırnak
    ''': "'",  # Sol tipografik tek tırnak
    ''': "'",  # Sağ tipografik tek tırnak
}

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Düzeltildi: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Hata: {filepath} - {e}")
        return False

# Tüm Python dosyalarını bul ve düzelt
fixed_count = 0
for filepath in glob.glob('**/*.py', recursive=True):
    if fix_file(filepath):
        fixed_count += 1

print(f"\n{fixed_count} dosya düzeltildi.")
