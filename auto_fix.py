import os
import shutil
import sys

from auto_fix_engine import fix_code


print("=" * 60)
print("               AI AUTO FIX AGENT")
print("=" * 60)
print()

# ==========================================
# Check Arguments
# ==========================================

if len(sys.argv) != 2:
    print("Usage:")
    print("python auto_fix.py <python_file>")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.isfile(filename):
    print(f"❌ File not found: {filename}")
    sys.exit(1)

# ==========================================
# Read File
# ==========================================

print(f"[✓] Reading file: {filename}")

with open(filename, "r", encoding="utf-8") as file:
    code = file.read()

print("✔ File loaded successfully.\n")

# ==========================================
# Create Backup
# ==========================================

backup_file = filename + ".bak"

shutil.copy2(filename, backup_file)

print(f"[✓] Backup created: {backup_file}\n")

# ==========================================
# AI Fix
# ==========================================

fixed_code = fix_code(code)

print("\n" + "=" * 60)
print("              GENERATED FIX")
print("=" * 60)
print()

print(fixed_code)

print()

print("=" * 60)
print("               FIX COMPLETED")
print("=" * 60)