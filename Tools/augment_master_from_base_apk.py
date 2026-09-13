#!/usr/bin/env python3
"""Add missing base-APK key files after placing com.estar.bap.zip next to this script or passing path arg."""
from pathlib import Path
import zipfile,sys
src=Path(sys.argv[1]) if len(sys.argv)>1 else Path('com.estar.bap.zip')
out=Path(sys.argv[2]) if len(sys.argv)>2 else Path('BASE_APK_RECOVERED_FILES')
out.mkdir(parents=True,exist_ok=True)
needed={
 'assets/bin/Data/Managed/Metadata/global-metadata.dat':'global-metadata.dat',
 'assets/bin/Data/data.unity3d':'data.unity3d',
 'assets/bin/Data/boot.config':'boot.config',
}
with zipfile.ZipFile(src) as z:
    for member,name in needed.items():
        if member in z.namelist(): (out/name).write_bytes(z.read(member)); print('OK',member)
        else: print('MISSING',member)
