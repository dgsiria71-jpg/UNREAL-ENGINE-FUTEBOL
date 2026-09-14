"""Join recovered spmove activation, selection, and param[2] data for GetVVer."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACCESS=ROOT/'Recovery/Normalized/spmove_modifier_access_static_trace.json'
RUNTIME=ROOT/'Recovery/Normalized/spmove_runtime_static_trace.json'
COLLECTED=ROOT/'Recovery/Normalized/spmove_collected_open_all.json'
CAL=ROOT/'Recovery/Normalized/cal_spmove_static_trace.json'
OUTPUT=ROOT/'Recovery/Normalized/getvver_spmove_runtime_ratios.json'

def sha(p): return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\r',b'\n')).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))

def analyze():
    access,runtime,collected,cal=map(load,(ACCESS,RUNTIME,COLLECTED,CAL))
    groups=runtime['property_logic_id_alignment']
    buckets={int(x['logic_id']):x['entries'] for x in collected['buckets']}
    writes={x['flag']:x for x in cal['confirmed_writes']}
    out={}
    activation={}
    for key,logic,flag in (('0x3FC',0x3FC,'ShootLongKick'),('0x41A',0x41A,'shootPush')):
        group=groups[key]
        rows=dict(zip(group['record_ids'],group['param_raw_by_level']))
        candidates=buckets[logic]
        selected=max(x['child_id'] for x in candidates)
        if selected not in rows: raise ValueError(f'{key} selected child {selected} has no normalized record')
        values=[row[2] for row in group['param_raw_by_level']]
        observed=access['modifier_accesses'][key+'_vver']['canonical_param_at_index']
        if values != observed: raise ValueError(f'{key} param[2] traces disagree')
        out[key]={
            'logic_id':logic,
            'levels':group['levels'],
            'record_ids':group['record_ids'],
            'param2_raw_by_level':values,
            'param2_factor_by_level':[v/1024 for v in values],
            'selection_rule':'highest signed child_id in the eligible runtime inventory; level/order/odds do not choose the winner',
        }
        activation[key]={
            'flag':flag,
            'flag_byte_offset':writes[flag]['byte_offset'],
            'cal_spmove_condition':writes[flag]['condition'],
            'getvver_additional_guard':'base vector magnitude >= 1 raw',
            'data_guard':'GetSpmoveDataRatio(logic_id, noRatio=true) returns a non-null list with index 2',
        }
    selected={}
    for key in ('0x3FC','0x41A'):
        logic=int(key,16); candidates=buckets[logic]; child=max(x['child_id'] for x in candidates)
        idx=out[key]['record_ids'].index(child)
        selected[key]={'selected_child_id':child,'selected_level':out[key]['levels'][idx], 'param2_raw':out[key]['param2_raw_by_level'][idx], 'factor':out[key]['param2_factor_by_level'][idx], 'scope':'open-all collected inventory fixture, not every player runtime inventory'}
    return {
      'schema_version':'football.recovery.getvver_spmove_runtime_ratios.v1',
      'source_build':'football-dream-be-a-pro-1-221-5',
      'sources':{p.relative_to(ROOT).as_posix():sha(p) for p in (ACCESS,RUNTIME,COLLECTED,CAL)},
      'modifiers':out,'activation':activation,'open_all_selection':selected,
      'order':['0x3FC','0x41A'],
      'composition':'each active modifier scales x/y/z independently with native fixed_mul; when both are active rounding occurs after each ordered multiply',
      'confirmed_scope':'activation gates, selection rule, level matrix, open-all selected records, and raw param[2] factors',
      'unknown':['actual eligible inventory for each runtime player/action','representative whole-GetVVer native output vectors','final GetKickVelocity and BALL_CONTACT binding'],
      'whole_getvver_equivalent':False,'physics_v0_3_gate':'BLOCKED',
      'next_gate':'build representative GetVVer differential vectors for none/0x3FC/0x41A/both using recovered upstream inputs and selected runtime inventories',
    }

def main():
    data=analyze(); OUTPUT.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n'); print(f"GETVVER_SPMOVE_RATIOS: GREEN output={OUTPUT} gate={data['physics_v0_3_gate']}"); return 0
if __name__=='__main__': raise SystemExit(main())
