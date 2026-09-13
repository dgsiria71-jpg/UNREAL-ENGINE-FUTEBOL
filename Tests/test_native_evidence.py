"""Ensure persisted native evidence rejects stale implementation or source data."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('native_evidence',ROOT/'Tools/check_native_evidence.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class EvidenceBindingTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  files={'Recovery/Normalized/spmove_normalized.json'}
  for name in module.REPORTS:
   rel='Recovery/Normalized/'+name;files.add(rel)
   report=json.loads((ROOT/rel).read_text(encoding='utf-8'))
   files.update(report.get('cpp_source_sha256',{}));files.update(report.get('verification_source_sha256',{}))
  files.update(['Tools/verify_native_vector_math.py','Tools/verify_spmove_branches.py'])
  for rel in files:
   out=self.root/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,out)
  self.assertEqual(module.validate(self.root),[])
 def test_producer_change_invalidates_bound_evidence(self):
  with (self.root/'Reference/FootballPhysics/SpmoveProducer.h').open('a') as f:f.write('\n// changed\n')
  errors=module.validate(self.root)
  self.assertTrue(any('native_spmove_producer_validation.json: stale source binding' in e for e in errors))
 def test_config_mutation_invalidates_selection_report(self):
  with (self.root/'Recovery/Normalized/spmove_normalized.json').open('a') as f:f.write(' ')
  self.assertTrue(any('stale normalized config binding' in e for e in module.validate(self.root)))
if __name__=='__main__':unittest.main()
