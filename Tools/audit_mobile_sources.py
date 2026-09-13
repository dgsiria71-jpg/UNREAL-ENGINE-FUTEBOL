"""Read-only critical-source inventory for the explicitly scoped 1-221-5 inputs."""
from pathlib import Path
import hashlib, io, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
VIDEO=Path(r'C:\Users\dg71\Videos\football-dream-be-a-pro-1-221-5')
DOWNLOAD=Path(r'C:\Users\dg71\Downloads')
CRITICAL={'libil2cpp.so','global-metadata.dat','data.unity3d','datapack.unity3d','controller.ctrl','spmoveconfig','spmoveactiondata','shootspeed','AndroidManifest.xml','manifest.json'}
records=[]; inventories=[]
def record(path,data,kind):
    records.append({'path':path,'kind':kind,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
def archive(z,label,depth=0):
    infos=z.infolist(); inventories.append({'path':label,'entries':len(infos),'uncompressed_bytes':sum(i.file_size for i in infos)})
    for i in infos:
        if i.is_dir():continue
        name=Path(i.filename).name
        if name in CRITICAL:record(label+'!/'+i.filename,z.read(i),name)
        if depth<3 and name.lower().endswith(('.zip','.apk')):
            data=z.read(i)
            record(label+'!/'+i.filename,data,'archive')
            with zipfile.ZipFile(io.BytesIO(data)) as nested:archive(nested,label+'!/'+i.filename,depth+1)
def scan(path):
    if path.is_dir():
        files=list(path.rglob('*')); inventories.append({'path':str(path),'files':sum(x.is_file() for x in files),'bytes':sum(x.stat().st_size for x in files if x.is_file())})
        for f in files:
            if f.is_file() and f.name in CRITICAL:record(str(f),f.read_bytes(),f.name)
        for f in sorted(path.glob('*.zip')):scan(f)
    else:
        with path.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
        records.append({'path':str(path),'kind':'archive','bytes':path.stat().st_size,'sha256':h})
        with zipfile.ZipFile(path) as z:archive(z,str(path))
    print('AUDITED',path,flush=True)
def main():
    scan(VIDEO)
    for f in [DOWNLOAD/'football-dream-be-a-pro-1-221-5.xapk',Path(r'C:\Users\dg71\Videos\football-dream-be-a-pro-1-221-5.zip'),DOWNLOAD/'FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip',ROOT/'.local/recovered-original/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip']:scan(f)
    groups={}
    for r in records:groups.setdefault((r['kind'],r['sha256']),[]).append(r['path'])
    result={'schema_version':'football.source_matrix.v1','build_scope':'1-221-5','future_build_consumed':False,'records':records,'inventories':inventories,'identical_groups':[{'kind':k,'sha256':h,'classification':'DUPLICATE_IDENTICAL_COPY','paths':v} for (k,h),v in groups.items() if len(v)>1],'note':'Different hashes require variant investigation; archive compression and CPU ABI differences are not by themselves different gameplay builds. Build labels do not replace package metadata.'}
    out=ROOT/'Recovery/Normalized/MOBILE_1_221_5_SOURCE_MATRIX.json';out.write_text(json.dumps(result,indent=2),encoding='utf-8');print('SOURCE_MATRIX',len(records),'records',len(result['identical_groups']),'duplicate groups')
if __name__=='__main__':main()
