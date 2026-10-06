import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
sys.dont_write_bytecode=True
def module(name):
    directory = (SCRIPTS.parent.parent/'uss-notes/scripts') if name in ('validate_vault','safe_publish') else (SCRIPTS.parent.parent/'uss-ingestion/scripts') if name == 'local_ocr_sidecar' else SCRIPTS
    spec=importlib.util.spec_from_file_location(name,directory/(name+'.py'))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
idx=module('build_source_index');cov=module('coverage_check');val=module('validate_vault');pub=module('safe_publish')
ocr=module('local_ocr_sidecar')
pack=module('chapter_pack')

class WorkflowTests(unittest.TestCase):
    def test_chapter_one_does_not_match_ten(self):
        self.assertTrue(pack.match_chapter({'inferred_chapter':'Ch1'},'Ch01'))
        self.assertFalse(pack.match_chapter({'inferred_chapter':'Ch10'},'Ch1'))

    def test_broken_anchor_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'a.md').write_text('# Actual\n[[a#missing]]\n[a](a.md#actual)','utf-8')
            self.assertEqual(len(val.find_broken_links(root,list(root.glob('*.md')))),1)

    def test_question_keeps_code_context(self):
        text='## 第 1 页\nQ1: What is arr?\n```java\nint[] a = {1};\n```'
        rows=idx.extract_questions(text,Path('a.md'),'a.md','teacher_ppt')
        self.assertIn('int[] a',rows[0]['context'])

    def test_ocr_page_order_and_duplicates(self):
        pages,_=ocr.normalize([{'page_index':1,'rec_texts':['second']},{'page_index':0,'rec_texts':['first']}],'ocr')
        self.assertIn('第 1 页',pages[0]);self.assertIn('first',pages[0])
        with self.assertRaises(ValueError):ocr.normalize([{'page_index':0},{'page_index':0}],'ocr')

    def test_question_locations(self):
        text='# Topic\n## 第 1 页\nQ1: What is arr?\n## 第 2 页\nQ1: What is arr?\n'
        rows=idx.extract_questions(text,Path('Ch1.md'),'Ch1.md','teacher_ppt')
        self.assertEqual(len(rows),2)
        self.assertNotEqual(rows[0]['id'],rows[1]['id'])
        self.assertTrue(all(x['status']=='candidate' for x in rows))

    def test_numbered_code_not_question(self):
        text='## 第 1 页\n1. int value = 3;\n2. System.out.println(value);\n```java\n// Question: why?\n```\n'
        self.assertEqual(idx.extract_questions(text,Path('Ch1.md'),'Ch1.md','teacher_ppt'),[])

    def test_lexical_hits_do_not_certify_coverage(self):
        self.assertNotEqual(cov.classify({'question':'Explain polymorphism'},[{'score':999,'text':'polymorphism'}]),'A')

    def test_stable_ids(self):
        a={'file':'a.md','heading_path':['第 1 页'],'text':'one'}
        first,_=idx.assign_chunk_ids_and_terms([a])
        second,_=idx.assign_chunk_ids_and_terms([{'file':'0.md','heading_path':['Other'],'text':'two'},a])
        self.assertEqual(first[0]['chunk_id'],next(x['chunk_id'] for x in second if x['file']=='a.md'))

    def test_incremental_keeps_progress(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);src=root/'src';src.mkdir();out=root/'index'
            (src/'Ch1.md').write_text('# Chapter\n## 第 1 页\nA useful topic about methods.','utf-8')
            cmd=[sys.executable,str(SCRIPTS/'build_source_index.py'),str(src),'--out',str(out)]
            subprocess.run(cmd,check=True,capture_output=True)
            p=out/'progress.json';state=json.loads(p.read_text('utf-8'));state['writing']={'chapter1':'reviewed'};p.write_text(json.dumps(state),'utf-8')
            (out/'questions.reviewed.jsonl').write_text('{"id":"human-review"}\n','utf-8')
            (src/'Ch2.md').write_text('# Another\nnew material','utf-8')
            subprocess.run(cmd,check=True,capture_output=True)
            self.assertEqual(json.loads(p.read_text('utf-8'))['writing'],{'chapter1':'reviewed'})
            self.assertIn('human-review',(out/'questions.reviewed.jsonl').read_text('utf-8'))

    def test_publish_preserves_human_edit(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);stage=root/'stage';vault=root/'vault';base=root/'baseline'
            for p in (stage,vault,base):p.mkdir()
            (base/'a.md').write_text('original','utf-8');(vault/'a.md').write_text('human edit','utf-8');(stage/'a.md').write_text('new version','utf-8')
            (stage/'b.md').write_text('new file','utf-8')
            result=pub.publish(stage,vault,root/'state.json',base,True)
            self.assertEqual(result['status'],'conflict')
            self.assertEqual((vault/'a.md').read_text('utf-8'),'human edit')
            self.assertFalse((vault/'b.md').exists())

    def test_publish_known_baseline_and_repeat(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);stage=root/'stage';vault=root/'vault';base=root/'baseline'
            for p in (stage,vault,base):p.mkdir()
            for p in (vault,base):(p/'a.md').write_text('original','utf-8')
            (stage/'a.md').write_text('new','utf-8')
            result=pub.publish(stage,vault,root/'state.json',base,True)
            self.assertTrue(result['applied']);self.assertEqual((vault/'a.md').read_text(),'new')
            self.assertEqual(pub.publish(stage,vault,root/'state.json')['changed'],0)

    def test_code_not_scanned_as_prose(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'a.md').write_text('```java\n<concept>\n// [[missing]]\n```\nInline `<concept>`','utf-8')
            report=val.validate(root,None,'lightweight')
            self.assertEqual(report['placeholder_hits'],[])
            self.assertEqual(report['broken_links'],[])

    def test_explicit_link_path_not_hidden_by_same_stem(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'a.md').write_text('[[wrong/topic]]\n[missing](gone.md)\n[valid](topic.md)','utf-8');(root/'topic.md').write_text('# Topic','utf-8')
            self.assertEqual(len(val.find_broken_links(root,list(root.glob('*.md')))),2)

if __name__=='__main__':unittest.main()
