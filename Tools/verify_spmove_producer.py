"""Native calSpmoveInUse differential; external query outcomes are explicit fixtures."""
import hashlib,json,random,struct,subprocess
from verify_native_vector_math import NativeVectorOracle,REGIONS,HALT
from verify_native_kernels import ROOT,BINARY,EXPECTED_SHA,TYPE_SLOT,TYPE_OBJECT,STACK,MASK64,digest,packed,signed32
from recover_native_sqrt_table import recover
from disassemble_spmove_runtime import file_offset
from unicorn import arm64_const as regs
PROBE=ROOT/'.local/build/reference/SpmoveProducerProbe.exe'
SPAN=(0x14C5548,0x14C5AA4)
RESET=(0x14E5A4C,0x14E5A5C)
HOOKS={0x1254100:'disturbance query',0x13B01DC:'goal collection membership',
 0x1968070:'Player.GetSpmoveData result including unresolved odds',
 0x1382664:'shoot ball position',0x16DB8F4:'CheckBallPos geometry',
 0x14DEFA8:'goal up position',0x14DEF74:'goal down position',0x14DF68C:'goal center',
 0x126C078:'angle helper',0x1FF58AC:'config singleton',0x1566AB4:'distance curve interpolation'}
GOT=[0x40EF420,0x40CD508,0x405B478,0x40928D8,0x40BC108]
OBJ=TYPE_SLOT+0x3000;OWNER=TYPE_SLOT+0x3400;PLAYER=TYPE_SLOT+0x3800
AREA=TYPE_SLOT+0x4000;CONFIG=TYPE_SLOT+0x4400
class Oracle(NativeVectorOracle):
 def __init__(self,blob,table):
  super().__init__(blob,table)
  def page(a):
   p=a&~0xfff
   if not any(s<=p<=e for s,e,_ in self.mu.mem_regions()):self.mu.mem_map(p,0x1000)
  for s,e in [SPAN,RESET]:
   for p in range(s&~0xfff,(e+0xfff)&~0xfff,4096):page(p)
   self.mu.mem_write(s,blob[file_offset(blob,s):file_offset(blob,e-4)+4])
  for a in HOOKS:page(a);self.mu.mem_write(a,blob[file_offset(blob,a):file_offset(blob,a)+4])
  for a in GOT:page(a);self.q(a,TYPE_SLOT)
  for a in [0x4366C5C,0x4365E1E,0x4365E20]:page(a);self.mu.mem_write(a,b'\x01')
  self.q(OBJ+0x20,OWNER);self.q(OBJ+0x28,OWNER);self.q(OWNER+0x1B0,PLAYER)
  self.q(OWNER+0x50,OWNER);self.q(OWNER+0x120,AREA);self.q(CONFIG+0xE8,CONFIG)
 def q(self,a,v):self.mu.mem_write(a,struct.pack('<Q',v))
 def i(self,a,v):self.mu.mem_write(a,struct.pack('<i',v))
 def get(self,n):return self.mu.reg_read(getattr(regs,'UC_ARM64_REG_'+n.upper()))
 def set(self,n,v):self.mu.reg_write(getattr(regs,'UC_ARM64_REG_'+n.upper()),v&MASK64)
 def ret(self,v):self.set('x0',v);self.set('pc',self.get('x30'))
 def guard(self,mu,a,size,_):
  if a in HOOKS:
   c=self.c
   if a==0x1254100:self.ret(c[2])
   elif a==0x13B01DC:self.ret(c[{15:4,32:5,16:6}[self.get('x1')]])
   elif a==0x1968070:
    key=self.get('x1');idx=[0x417,0x41A,0x418,0x3FC,0x3FB,0x40B].index(key)
    if self.get('x0')!=PLAYER:raise AssertionError('property owner mismatch')
    self.queries|=1<<idx;self.ret(CONFIG if c[16]&(1<<idx) else 0)
   elif a in (0x1382664,0x16DB8F4):self.ret(packed(c[7],c[8]))
   elif a in (0x14DEFA8,0x14DEF74):self.ret(0)
   elif a==0x14DF68C:self.ret(packed(c[9],c[10]))
   elif a==0x126C078:self.ret(c[11])
   elif a==0x1FF58AC:self.ret(CONFIG)
   elif a==0x1566AB4:self.distance=signed32(self.get('x1'));self.ret(c[15])
   return
  if size!=4 or not any(s<=a<e for s,e in [SPAN,RESET]+REGIONS):raise RuntimeError(f'unexpected instruction {a:#x}')
 def evaluate(self,c):
  self.c=c;self.queries=0;self.distance=None
  for i in range(31):self.set(f'x{i}',0)
  self.set('nzcv',0);self.set('sp',STACK);self.set('x30',HALT)
  self.set('x0',OBJ);self.set('x1',c[0]);self.set('x2',c[1])
  self.i(TYPE_SLOT+0x408,c[3])
  for offset,value in zip([0x170,0x174,0x178],c[12:15]):self.i(CONFIG+offset,value)
  self.mu.mem_write(OBJ+0xA8,b'\xff'*7)
  self.mu.emu_start(SPAN[0],HALT,count=4096)
  if self.get('pc')!=HALT or self.distance is None:raise RuntimeError('producer failed to finish')
  return [*self.mu.mem_read(OBJ+0xA8,7),self.distance,self.queries]
def corpus():
 rng=random.Random(0xCA15)
 values=[-2147483648,-1025,-1,0,1,1024,1025,2147483647]
 for available in range(64):
  for membership in [0,1,2,3,255]:
   for curve in [1024,1025]:
    yield [0x16B3,255,1,0,membership,membership,membership,3072,4096,0,0,100,101,3073,4095,curve,available]
 for _ in range(2000):
  yield [rng.choice([0,0x16B3,0x16B6,0x16B4]),rng.randrange(256),rng.choice(values),rng.choice(values),
         *(rng.randrange(4) for _ in range(3)),*(rng.choice(values) for _ in range(9)),rng.randrange(64)]
def main():
 blob=BINARY.read_bytes();assert hashlib.sha256(blob).hexdigest()==EXPECTED_SHA
 table=recover();oracle=Oracle(blob,table['values']);cases=list(corpus());expected=[oracle.evaluate(c) for c in cases]
 sources=['Reference/FootballCore/FixedPoint.h','Reference/FootballPhysics/NativeVectorMath.h','Reference/FootballPhysics/NativeSqrtTable.h','Reference/FootballPhysics/SpmoveProducer.h','Tests/spmove_producer_probe.cpp']
 if not PROBE.is_file() or any((ROOT/p).stat().st_mtime>PROBE.stat().st_mtime for p in sources):raise RuntimeError('rebuild probe')
 payload=''.join(' '.join(map(str,c))+'\n' for c in cases)
 result=subprocess.run([str(PROBE)],input=payload,text=True,capture_output=True,check=True)
 actual=[list(map(int,line.split())) for line in result.stdout.splitlines()]
 assert len(actual)==len(expected)
 for c,a,b in zip(cases,expected,actual):
  if a!=b:raise AssertionError(f'case={c} native={a} cpp={b}')
 report={'schema_version':'football.recovery.native_spmove_producer.v1','cases':len(cases),'mismatches':0,
 'binary_sha256':EXPECTED_SHA,'metadata_sha256':table['metadata_sha256'],'native_span':list(map(hex,SPAN)),
 'hooked_boundaries':{hex(a):n for a,n in HOOKS.items()},'cpp_source_sha256':{p:digest(ROOT/p) for p in sources},
 'verification_source_sha256':{p:digest(ROOT/p) for p in ['Tools/verify_spmove_producer.py','Tools/verify_native_vector_math.py','Tools/verify_native_kernels.py','Tools/recover_native_sqrt_table.py','Tools/disassemble_spmove_runtime.py']},
 'input_sha256':hashlib.sha256(payload.encode()).hexdigest(),'native_output_sha256':hashlib.sha256(json.dumps(expected).encode()).hexdigest(),
 'cpp_executable_sha256':digest(PROBE),'physics_v0_3_gate':'blocked',
 'scope':'Original reset and full producer control flow, squared distance/sqrt, flags and property query set. External geometry, collection membership, curve interpolation and GetSpmoveData odds outcomes are supplied; not full eligibility proof.'}
 (ROOT/'Recovery/Normalized/native_spmove_producer_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(f'NATIVE_SPMOVE_PRODUCER: {len(cases)}/{len(cases)} MATCH')
if __name__=='__main__':main()
