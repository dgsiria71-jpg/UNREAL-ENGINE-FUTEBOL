"""Execute native spmove selector + modifiers using inventory/config snapshots.

No GetSpmoveData/selector winner is hooked. Ordinary collection operations,
allocation, singleton lookup and diagnostic formatting are adapted to fixtures.
The upstream getSpmoveIdDict COLLECTOR is the remaining explicit state boundary.
"""
import hashlib
import json
import random
import struct
import subprocess
from pathlib import Path
from verify_spmove_branches import NativeBranches, SPANS, PROPERTY, PLAYER
from verify_native_vector_math import REGIONS, HALT
from verify_native_kernels import ROOT, BINARY, EXPECTED_SHA, TYPE_SLOT, STACK, MASK32, MASK64, digest, signed32
from recover_native_sqrt_table import recover
from disassemble_spmove_runtime import file_offset
from unicorn import arm64_const as regs

PROBE=ROOT/'.local/build/reference/SpmoveSelectionProbe.exe'
HEAP=0xA000000
MANAGER=HEAP+0x100
INVENTORY_DICT=HEAP+0x200
MODULE=HEAP+0x300
CONFIG_DICT=HEAP+0x400
METHODS={
 'max_id':(0x1B72FD4,0x1B73100),
 'max_config':(0x1B7264C,0x1B726C0),
 'config_by_logic':(0x1B72794,0x1B72814),
 'data_no_ratio':(0x1B72814,0x1B72848),
 'ids':(0x1B72DA8,0x1B72E40),
 'module_config':(0x1449858,0x1449940),
 'player_data':(PROPERTY,PROPERTY+16),
}
HOOKS={
 0x1B71AAC:'getSpmoveIdDict snapshot',
 0x2C6A4F8:'Dictionary.ContainsKey',0x2C6A188:'Dictionary.get_Item',
 0x2C6BE94:'Dictionary.TryGetValue',0x1E34BE4:'SpmoveModule singleton',
 0x11C6780:'object allocation',0x14494F4:'empty SpmoveIDCombine constructor',
 0x2F2737C:'List.GetEnumerator',0x1C2BC58:'List.Enumerator.MoveNext',
 0x1C2BC54:'List.Enumerator.Dispose',0x11C6774:'diagnostic boxing',
 0x215A3FC:'diagnostic formatting',0x29E1700:'diagnostic logging',
}
GOT_SLOTS=[0x40DC650,0x40D26D8,0x4076588,0x4104FF8,0x40C8238,
           0x409D760,0x412BA60,0x4124D78,0x41001E8,0x407F458,0x40EA748]


class NativeSelection(NativeBranches):
    def __init__(self,blob,table):
        self.inventory={}
        self.configs={}
        self.active='vhor_a'
        self.calls={}
        self.config_reads=[]
        self.cursor=HEAP+0x1000
        super().__init__(blob,table)
        self.mu.mem_map(HEAP,0x200000)
        def ensure_page(address):
            page=address&~0xFFF
            if not any(s<=page<=e for s,e,_ in self.mu.mem_regions()):self.mu.mem_map(page,0x1000)
        for start,end in METHODS.values():
            for page in range(start&~0xFFF,(end+0xFFF)&~0xFFF,0x1000):ensure_page(page)
            self.mu.mem_write(start,blob[file_offset(blob,start):file_offset(blob,end-4)+4])
        for address in HOOKS:
            ensure_page(address)
            self.mu.mem_write(address,blob[file_offset(blob,address):file_offset(blob,address)+4])
        for slot in GOT_SLOTS:
            ensure_page(slot)
            self.mu.mem_write(slot,struct.pack('<Q',TYPE_SLOT))
        ensure_page(0x4366963)
        self.mu.mem_write(0x4366963,b'\x01')
        for flag in (0x4369E80,0x4369E82,0x4369E83,0x4369E84):
            self.mu.mem_write(flag,b'\x01')
        self.mu.mem_write(PLAYER+0x28,struct.pack('<Q',MANAGER))
        self.mu.mem_write(MODULE+0x18,struct.pack('<Q',CONFIG_DICT))

    def allocate(self,size):
        result=self.cursor
        self.cursor=(self.cursor+size+15)&~15
        if self.cursor>=HEAP+0x200000:raise RuntimeError('Fixture heap exhausted')
        self.mu.mem_write(result,bytes(size))
        return result

    def read_q(self,address):return struct.unpack('<Q',self.mu.mem_read(address,8))[0]
    def read_i(self,address):return struct.unpack('<i',self.mu.mem_read(address,4))[0]
    def write_q(self,address,value):self.mu.mem_write(address,struct.pack('<Q',value))
    def return_value(self,value=0):
        self.set('x0',value)
        self.set('pc',self.get('x30'))

    def guard(self,mu,address,size,_):
        if address in HOOKS:
            name=HOOKS[address]
            self.calls[name]=self.calls.get(name,0)+1
            if address==0x1B71AAC:
                if self.get('x0')!=MANAGER:raise AssertionError('wrong inventory owner')
                self.return_value(INVENTORY_DICT)
            elif address in (0x2C6A4F8,0x2C6A188):
                if self.get('x0')!=INVENTORY_DICT:raise AssertionError('wrong inventory dictionary')
                key=signed32(self.get('x1'))
                self.return_value(int(key in self.inventory) if address==0x2C6A4F8 else self.inventory[key])
            elif address==0x2C6BE94:
                if self.get('x0')!=CONFIG_DICT:raise AssertionError('wrong config dictionary')
                key=signed32(self.get('x1'))
                self.config_reads.append(key)
                self.write_q(self.get('x2'),self.configs.get(key,0))
                self.return_value(int(key in self.configs))
            elif address==0x1E34BE4:self.return_value(MODULE)
            elif address==0x11C6780:self.return_value(self.allocate(0x20))
            elif address==0x14494F4:
                if self.read_i(self.get('x0')+0x10) or self.read_i(self.get('x0')+0x14):
                    raise AssertionError('expected zero initialized fields')
                self.return_value()
            elif address==0x2F2737C:
                # IL2CPP enumerator return struct: list,index,version,current.
                self.mu.mem_write(self.get('x8'),struct.pack('<QiiQ',self.get('x0'),0,0,0))
                self.return_value()
            elif address==0x1C2BC58:
                p=self.get('x0')
                array_list,index,version,_=struct.unpack('<QiiQ',self.mu.mem_read(p,24))
                if version!=0:raise AssertionError('fixture enumerator version changed')
                count=self.read_i(array_list+0x18)
                if index<count:
                    array=self.read_q(array_list+0x10)
                    item=self.read_q(array+0x20+index*8)
                    self.mu.mem_write(p,struct.pack('<QiiQ',array_list,index+1,version,item))
                    self.return_value(1)
                else:
                    self.mu.mem_write(p,struct.pack('<QiiQ',array_list,count+1,version,0))
                    self.return_value(0)
            elif address==0x1C2BC54:self.return_value()
            elif address in (0x11C6774,0x215A3FC):self.return_value(self.allocate(0x20))
            else:self.return_value()
            return
        if address==PROPERTY:
            if self.get('x0')!=PLAYER:raise AssertionError('wrong Player owner')
            self.lookups.append(self.get('x1'))
        allowed=list(METHODS.values())+REGIONS
        if self.active in SPANS:allowed.append(SPANS[self.active])
        if size!=4 or not any(s<=address<e for s,e in allowed):
            raise RuntimeError(f'unexpected native instruction {address:#x}')

    def list_fixture(self,values,objects=False):
        pointer=self.allocate(0x20)
        items=self.allocate(0x20+len(values)*(8 if objects else 4))
        self.write_q(pointer+0x10,items)
        self.mu.mem_write(pointer+0x18,struct.pack('<i',len(values)))
        for i,value in enumerate(values):
            self.mu.mem_write(items+0x20+i*(8 if objects else 4),struct.pack('<Q' if objects else '<i',value))
        return pointer

    def fixture(self,case):
        self.cursor=HEAP+0x1000
        self.inventory={}
        self.configs={}
        self.calls={}
        self.config_reads=[]
        for key,candidates in case['inventory'].items():
            values=[]
            for child,father in candidates:
                item=self.allocate(0x20)
                self.mu.mem_write(item+0x10,struct.pack('<ii',child,father))
                values.append(item)
            self.inventory[int(key)]=self.list_fixture(values,True)
        for row in case['configs']:
            record=self.allocate(0x50)
            self.mu.mem_write(record+0x18,struct.pack('<ii',row['id'],row['enabled']))
            self.mu.mem_write(record+0x30,struct.pack('<ii',row['level'],row['odds']))
            self.mu.mem_write(record+0x48,struct.pack('<i',row['order']))
            if row['params'] is not None:self.write_q(record+0x10,self.list_fixture(row['params']))
            self.configs[row['id']]=record

    def evaluate(self,case):
        self.fixture(case)
        op=case['op']
        self.active=op
        if op in SPANS:
            # Parent sets input vector/registers. Its selected-list fixtures are
            # empty and ignored: the real Player->manager chain executes now.
            v=self.branch(op,case['flags'],0,*case['vector'],0,0,0,0)
            return ' '.join(map(str,v))
        for i in range(31):self.set(f'x{i}',0)
        self.set('nzcv',0)
        self.set('sp',STACK)
        self.set('x30',HALT)
        self.mu.mem_write(STACK-0x200,bytes(0x400))
        if op=='max':
            start=METHODS['max_id'][0]
            self.set('x0',MANAGER)
            self.set('x1',self.inventory[case['query']])
            self.set('x2',case['show_father'])
        elif op=='config':
            start=METHODS['config_by_logic'][0]
            self.set('x0',MANAGER)
            self.set('x1',case['query'])
        else:
            start=PROPERTY
            self.set('x0',PLAYER)
            self.set('x1',case['query'])
            self.set('x2',case['no_ratio'])
        self.mu.emu_start(start,HALT,count=10000)
        if self.get('pc')!=HALT:raise RuntimeError('native selector did not return')
        result=self.get('x0')
        if op=='max':return str(signed32(result))
        if not result:return 'NULL'
        if op=='config':return str(self.read_i(result+0x18))
        count=self.read_i(result+0x18)
        array=self.read_q(result+0x10)
        values=[self.read_i(array+0x20+i*4) for i in range(count)]
        return 'P '+str(count)+(' '+' '.join(map(str,values)) if values else '')


def base(op,inventory,configs,query=1022,no_ratio=1,show_father=0,flags=0,vector=(0,0,0)):
    return dict(op=op,inventory=inventory,configs=configs,query=query,no_ratio=no_ratio,
                show_father=show_father,flags=flags,vector=vector)


def synthetic_config(id,params=None,level=1,order=1,odds=100,enabled=1):
    return dict(id=id,params=params,level=level,order=order,odds=odds,enabled=enabled)


def corpus():
    rng=random.Random(0x53454C454354)
    groups={'max':[],'config':[],'params':[],'canonical_modifiers':[]}
    candidates=[[],[(10,0)],[(10,90),(20,0),(20,80),(20,70)],
                [(-2147483648,99)],[(-2147483647,99)],[(2147483647,-1)],
                [(100,2),(99,900)],[(4,0),(4,90),(4,-1)]]
    for _ in range(400):
        candidates.append([(rng.choice([-2147483648,-2147483647,-10,0,1,10,20,2147483647]),
                            rng.choice([-10,0,1,100,1000])) for _ in range(rng.randrange(12))])
    for rows in candidates:
        for show in (0,1,2,255):groups['max'].append(base('max',{1022:rows},[],show_father=show))
    for i in range(400):
        children=[rng.randint(1,20) for _ in range(rng.randrange(8))]
        inv={1022:[(id,rng.randint(0,100)) for id in children]} if i%7 else {}
        ids=list(set(children))
        rng.shuffle(ids)
        cfg=[synthetic_config(id,None if rng.randrange(4)==0 else [rng.randint(-5000,5000) for _ in range(rng.randrange(4))],
                              level=rng.randrange(20),order=rng.randrange(10),odds=rng.choice([0,100]),enabled=rng.randrange(2))
             for id in ids if rng.randrange(4)!=0]
        groups['config'].append(base('config',inv,cfg))
        for flag in (0,1,2,3,255):groups['params'].append(base('params',inv,cfg,no_ratio=flag))
    normalized=json.loads((ROOT/'Recovery/Normalized/spmove_normalized.json').read_text())
    rows=[r for r in normalized['canonical_source']['config']['records'] if r['logic_id'] in (0x3FE,0x3FC,0x41A,0x3FB)]
    configs=[synthetic_config(r['id'],r['param_raw'] if r['enable'] else None,r['level'],r['order'],r['odds'],r['enable']) for r in rows]
    flag_cases=[0,1,1<<24,1<<40,1<<32,(1<<56)-1,(1<<24)|(1<<40),1|(1<<40)]
    for _ in range(160):
        inv={}
        for logic in (0x3FE,0x3FC,0x41A,0x3FB):
            available=[r['id'] for r in rows if r['logic_id']==logic]
            rng.shuffle(available)
            inv[logic]=[(id,0) for id in available[:rng.randrange(6)]]
        vector=rng.choice([(0,0,0),(1,-1,1),(3072,4096,0),(0,24000,0),(-12000,500,-7000)])
        flags=rng.choice(flag_cases)
        for op in SPANS:groups['canonical_modifiers'].append(base(op,inv,configs,flags=flags,vector=vector))
    return groups


def serialize(case):
    fields=[case['op'],case['query'],case['no_ratio'],case['show_father'],case['flags'],*case['vector'],len(case['inventory'])]
    for key,rows in case['inventory'].items():
        fields.extend([key,len(rows)])
        for child,father in rows:fields.extend([child,father])
    fields.append(len(case['configs']))
    for row in case['configs']:
        params=row['params']
        fields.extend([row['id'],row['level'],row['order'],row['odds'],row['enabled'],-1 if params is None else len(params)])
        if params:fields.extend(params)
    return ' '.join(map(str,fields))+'\n'


def main():
    blob=BINARY.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=EXPECTED_SHA:raise ValueError('canonical binary mismatch')
    table=recover()
    sources=['Reference/FootballCore/FixedPoint.h',*[str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'Reference/FootballPhysics').glob('*.h')],
             'Tests/spmove_selection_probe.cpp']
    if not PROBE.is_file() or any((ROOT/p).stat().st_mtime>PROBE.stat().st_mtime for p in sources):
        raise RuntimeError('Run Tools/build_reference.cmd first')
    oracle=NativeSelection(blob,table['values'])
    groups={}
    for name,cases in corpus().items():
        expected=[oracle.evaluate(case) for case in cases]
        payload=''.join(map(serialize,cases))
        p=subprocess.run([str(PROBE)],input=payload,text=True,capture_output=True,check=True)
        actual=p.stdout.splitlines()
        if len(actual)!=len(expected):raise AssertionError('probe output count mismatch')
        for index,(a,b) in enumerate(zip(expected,actual)):
            if a!=b:raise AssertionError(f'{name} case={cases[index]} native={a!r} cpp={b!r}')
        groups[name]={'cases':len(cases),'mismatches':0,
                      'input_sha256':hashlib.sha256(payload.encode()).hexdigest(),
                      'native_output_sha256':hashlib.sha256(json.dumps(expected).encode()).hexdigest()}
        print(f'NATIVE_SPMOVE_SELECTION {name}: {len(cases)}/{len(cases)} MATCH')
    report={'schema_version':'football.recovery.native_spmove_selection.v1',
            'status':'inventory_snapshot_selection_and_modifiers_differential_pass',
            'binary_sha256':EXPECTED_SHA,'metadata_sha256':table['metadata_sha256'],
            'cases':sum(g['cases'] for g in groups.values()),'groups':groups,
            'native_methods':{n:{'start':hex(s),'end_exclusive':hex(e)} for n,(s,e) in METHODS.items()},
            'hooked_boundaries':{hex(k):v for k,v in HOOKS.items()},
            'cpp_source_sha256':{p:digest(ROOT/p) for p in sources},
            'verification_source_sha256':{p:digest(ROOT/p) for p in ['Tools/verify_spmove_selection.py','Tools/verify_spmove_branches.py',
              'Tools/verify_native_vector_math.py','Tools/verify_native_kernels.py','Tools/recover_native_sqrt_table.py','Tools/disassemble_spmove_runtime.py']},
            'normalized_config_sha256':hashlib.sha256((ROOT/'Recovery/Normalized/spmove_normalized.json').read_bytes()).hexdigest(),
            'cpp_executable_sha256':digest(PROBE),'text_digest_canonicalization':'UTF-8 without BOM, LF line endings',
            'confirmed':['highest signed child ID, not level/order/odds','showFather positive tie preference and return',
                         'noRatio low bit controls parameter return without RNG','missing maximum config does not fall back to lower candidates',
                         'inventory -> native selection -> canonical parameters -> modifier execution'],
            'excluded':['getSpmoveIdDict inventory collection/cache/eligibility','calSpmoveInUse producer','full GetVHor/GetVVer bases','GetKickVelocity/BALL_CONTACT'],
            'physics_v0_3_gate':'blocked'}
    (ROOT/'Recovery/Normalized/native_spmove_selection_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'NATIVE_SPMOVE_SELECTION_DIFFERENTIAL: {report["cases"]}/{report["cases"]} MATCH')


if __name__=='__main__':main()
