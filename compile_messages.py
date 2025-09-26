import os
from pathlib import Path
import polib

BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / 'locale'

def compile_locale(lang: str):
    po_path = LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'
    mo_path = LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.mo'
    if not po_path.exists():
        print(f"[skip] {po_path} not found")
        return
    po = polib.pofile(str(po_path))
    mo_bytes = po.to_binary()
    mo_path.write_bytes(mo_bytes)
    print(f"[ok] Compiled {po_path} -> {mo_path}")

if __name__ == '__main__':
    if not LOCALE_DIR.exists():
        print("No locale directory")
        raise SystemExit(0)
    for lang_dir in sorted(d.name for d in LOCALE_DIR.iterdir() if d.is_dir()):
        compile_locale(lang_dir)


