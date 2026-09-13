"""Reject native-validation reports whose bound C++ source has since changed."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORTS=['native_kernel_validation.json','native_vector_validation.json',
         'native_spmove_branch_validation.json','native_spmove_selection_validation.json','native_spmove_producer_validation.json']


def text_digest(path):
    data=path.read_bytes().decode('utf-8-sig').replace('\r\n','\n').encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def validate(root=ROOT):
    errors=[]
    for name in REPORTS:
        report_path=root/'Recovery/Normalized'/name
        if not report_path.is_file():
            errors.append('missing native validation report: '+name)
            continue
        report=json.loads(report_path.read_text(encoding='utf-8'))
        if report.get('physics_v0_3_gate')!='blocked':
            errors.append(name+': subset evidence cannot close v0.3')
        for relative,expected in {**report.get('cpp_source_sha256',{}), **report.get('verification_source_sha256',{})}.items():
            source=root/relative
            if not source.is_file() or text_digest(source)!=expected:
                errors.append(name+': stale source binding '+relative)
        if 'normalized_config_sha256' in report:
            config=root/'Recovery/Normalized/spmove_normalized.json'
            if hashlib.sha256(config.read_bytes()).hexdigest()!=report['normalized_config_sha256']:
                errors.append(name+': stale normalized config binding')
        if 'tool_sha256' in report:
            tool={'native_vector_validation.json':'Tools/verify_native_vector_math.py',
                  'native_spmove_branch_validation.json':'Tools/verify_spmove_branches.py'}[name]
            if text_digest(root/tool)!=report['tool_sha256']:
                errors.append(name+': stale verifier binding '+tool)
    return errors


if __name__=='__main__':
    errors=validate()
    for error in errors:print('NATIVE_EVIDENCE_ERROR: '+error)
    if errors:raise SystemExit(1)
    print('NATIVE_EVIDENCE_BINDINGS: CURRENT (source hashes; subset scope)')
