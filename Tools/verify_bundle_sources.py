#!/usr/bin/env python3
from pathlib import Path
import hashlib, zipfile
root=Path(__file__).resolve().parents[1]
for p in sorted((root/'00_SOURCE_ARCHIVES').glob('*.zip')):
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    with zipfile.ZipFile(p) as z: bad=z.testzip()
    print(p.name, h, 'ZIP_OK' if bad is None else 'BAD:'+str(bad))
