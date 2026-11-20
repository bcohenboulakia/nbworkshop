"""Integration checks with an isolated bare remote and temporary git clones."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / '.github' / 'scripts' / 'nbworkshop_publish.py'
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location('nbworkshop_publish', SCRIPT)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def git(*args, cwd=None):
    return subprocess.run(['git', *map(str, args)], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout.strip()


class PublishIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.remote = self.base / 'remote.git'
        git('init', '--bare', str(self.remote))
        self.repo = self.base / 'main'
        git('clone', str(self.remote), str(self.repo))
        git('config', 'user.email', 'test@example.com', cwd=self.repo)
        git('config', 'user.name', 'Test', cwd=self.repo)
        git('checkout', '-b', 'main', cwd=self.repo)
        (self.repo / 'notebooks').mkdir()
        (self.repo / 'notebooks' / 'Unit_Tutor.ipynb').write_text('{"cells": []}\n')
        (self.repo / 'notebooks' / 'Unit_Student.ipynb').write_text('{"cells": ["student"]}\n')
        git('add', '.', cwd=self.repo)
        git('commit', '-m', 'Initial source', cwd=self.repo)
        git('push', '-u', 'origin', 'main', cwd=self.repo)
        self.config = {'notebooks_dir': ['notebooks/'], 'tutor_postfix': '_Tutor',
                       'student_postfix': '_Student', 'generate_zip': True, 'rebuild_all': False}
        self.summary = self.base / 'summary.md'
        self.summary.write_text('## Student conversion\n', encoding='utf-8')
        self.plan = {'convert': ['notebooks/Unit_Tutor.ipynb'], 'deleted': []}
        self.zip = self.repo / 'notebooks/ZIP/Unit_Tutor.zip'
        self.zip.parent.mkdir()
        self.zip.write_bytes(b'zip-content')

    def publish(self, **kwargs):
        return publisher.publish(self.config, self.plan, self.repo, self.summary, **kwargs)

    def remote_file(self, path):
        git('fetch', 'origin', 'Students', cwd=self.repo)
        return git('show', 'FETCH_HEAD:' + path, cwd=self.repo)

    def other_commit(self, path='slides/course.pdf', content='ppt-pdf'):
        other = self.base / 'other'
        if not other.exists():
            git('clone', str(self.remote), str(other))
            git('config', 'user.email', 'test@example.com', cwd=other)
            git('config', 'user.name', 'Test', cwd=other)
        git('fetch', 'origin', 'Students', cwd=other)
        git('checkout', '-B', 'Students', 'FETCH_HEAD', cwd=other)
        f = other / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding='utf-8')
        git('add', path, cwd=other)
        git('commit', '-m', 'Concurrent publication', cwd=other)
        git('push', 'origin', 'Students', cwd=other)

    def test_orphan_students_contains_only_student_outputs(self):
        out = self.publish()
        self.assertEqual(out['status'], 'published')
        self.assertIn('student', self.remote_file('notebooks/Unit_Student.ipynb'))
        self.assertEqual(self.remote_file('README.md'), '## Student conversion')
        self.assertEqual(self.remote_file('notebooks/ZIP/Unit_Tutor.zip'), 'zip-content')
        paths = git('ls-tree', '-r', '--name-only', 'FETCH_HEAD', cwd=self.repo).splitlines()
        self.assertNotIn('notebooks/Unit_Tutor.ipynb', paths)


    def test_attached_files_published_without_copying_other_sources(self):
        source = self.repo / 'notebooks/Unit_Student.ipynb'
        source.write_text(json.dumps({'cells': [], 'metadata': {'attached_files': ['img/diagram.png']}}))
        image = self.repo / 'notebooks/img/diagram.png'
        image.parent.mkdir()
        image.write_bytes(b'fake-png')
        self.publish()
        self.assertEqual(self.remote_file('notebooks/img/diagram.png'), 'fake-png')
        git('fetch', 'origin', 'Students', cwd=self.repo)
        paths = git('ls-tree', '-r', '--name-only', 'FETCH_HEAD', cwd=self.repo).splitlines()
        self.assertNotIn('notebooks/Unit_Tutor.ipynb', paths)

    def test_zip_disabled_removes_only_previous_zip(self):
        self.publish()
        self.other_commit()
        self.config['generate_zip'] = False
        self.publish()
        git('fetch', 'origin', 'Students', cwd=self.repo)
        paths = git('ls-tree', '-r', '--name-only', 'FETCH_HEAD', cwd=self.repo).splitlines()
        self.assertNotIn('notebooks/ZIP/Unit_Tutor.zip', paths)
        self.assertIn('slides/course.pdf', paths)
        self.assertIn('notebooks/Unit_Student.ipynb', paths)

    def test_attached_resource_in_parent_directory(self):
        source = self.repo / 'notebooks/Unit_Student.ipynb'
        source.write_text(json.dumps({'cells': [], 'metadata': {'attached_files': ['../shared/chart.png']}}))
        asset = self.repo / 'shared/chart.png'
        asset.parent.mkdir()
        asset.write_text('shared-chart')
        self.publish()
        self.assertEqual(self.remote_file('shared/chart.png'), 'shared-chart')

    def test_preserve_pdf_on_rebuild_and_update_student(self):
        self.publish()
        self.other_commit()
        (self.repo / 'notebooks/Unit_Student.ipynb').write_text('{"cells": ["New student"]}')
        self.publish()
        self.assertEqual(self.remote_file('slides/course.pdf'), 'ppt-pdf')
        self.assertIn('New student', self.remote_file('notebooks/Unit_Student.ipynb'))

    def test_deletion_only_removes_notebook_owned_files(self):
        self.publish()
        self.other_commit()
        self.plan = {'convert': [], 'deleted': ['notebooks/Unit_Tutor.ipynb']}
        self.publish()
        git('fetch', 'origin', 'Students', cwd=self.repo)
        paths = git('ls-tree', '-r', '--name-only', 'FETCH_HEAD', cwd=self.repo).splitlines()
        self.assertNotIn('notebooks/Unit_Student.ipynb', paths)
        self.assertNotIn('notebooks/ZIP/Unit_Tutor.zip', paths)
        self.assertIn('slides/course.pdf', paths)

    def test_simultaneous_different_paths_retry_without_hooks(self):
        self.publish()
        original = publisher.publish_outputs._push
        calls = []

        def competing(repo, worktree, branch):
            calls.append('attempt')
            if len(calls) == 1:
                self.other_commit('slides/new.pdf', 'new-pdf')
            return original(repo, worktree, branch)

        (self.repo / 'notebooks/Unit_Student.ipynb').write_text('{"cells": ["Updated"]}')
        with patch.object(publisher.publish_outputs, '_push', side_effect=competing):
            outcome = self.publish()
        self.assertEqual(outcome['attempts'], 2)
        self.assertEqual(self.remote_file('slides/new.pdf'), 'new-pdf')
        self.assertIn('Updated', self.remote_file('notebooks/Unit_Student.ipynb'))

    def test_simultaneous_first_publication_after_other_tool_creates_branch(self):
        (self.repo / 'README.md').write_text('Instructor README')
        git('add', 'README.md', cwd=self.repo)
        git('commit', '-m', 'Source README', cwd=self.repo)
        git('push', 'origin', 'main', cwd=self.repo)
        real_push = publisher.publish_outputs._push
        attempts = []

        def create_students_first(repo, worktree, branch):
            attempts.append('attempt')
            if len(attempts) == 1:
                other = self.base / 'other'
                git('clone', str(self.remote), str(other))
                git('config', 'user.email', 'test@example.com', cwd=other)
                git('config', 'user.name', 'Test', cwd=other)
                git('checkout', '-b', 'Students', 'origin/main', cwd=other)
                pdf = other / 'slides/course.pdf'
                pdf.parent.mkdir(parents=True)
                pdf.write_text('ppt-first')
                git('add', 'slides/course.pdf', cwd=other)
                git('commit', '-m', 'PPTAnim publishes first', cwd=other)
                git('push', 'origin', 'Students', cwd=other)
            return real_push(repo, worktree, branch)

        with patch.object(publisher.publish_outputs, '_push', side_effect=create_students_first):
            outcome = self.publish()
        self.assertEqual(outcome['attempts'], 2)
        self.assertEqual(self.remote_file('slides/course.pdf'), 'ppt-first')
        self.assertEqual(self.remote_file('README.md'), '## Student conversion')

    def test_conflicting_publication_refused(self):
        self.publish()
        original = publisher.publish_outputs._push
        calls = []

        def competing(repo, worktree, branch):
            calls.append('attempt')
            if len(calls) == 1:
                self.other_commit('notebooks/Unit_Student.ipynb', 'Other update')
            return original(repo, worktree, branch)

        (self.repo / 'notebooks/Unit_Student.ipynb').write_text('{"cells": ["Our update"]}')
        with patch.object(publisher.publish_outputs, '_push', side_effect=competing):
            with self.assertRaisesRegex(RuntimeError, 'Concurrent changes'):
                self.publish()
        self.assertEqual(self.remote_file('notebooks/Unit_Student.ipynb'), 'Other update')

    def test_select_changed_and_deleted_only(self):
        base = git('rev-parse', 'HEAD', cwd=self.repo)
        (self.repo / 'notebooks/Unit_Tutor.ipynb').write_text('Changed input')
        (self.repo / 'notebooks/deleted.ipynb').write_text('Existing')
        git('add', '.', cwd=self.repo)
        git('commit', '-m', 'More sources', cwd=self.repo)
        base = git('rev-parse', 'HEAD', cwd=self.repo)
        (self.repo / 'notebooks/Unit_Tutor.ipynb').write_text('Changed again')
        (self.repo / 'notebooks/deleted.ipynb').unlink()
        git('add', '-A', cwd=self.repo)
        git('commit', '-m', 'Delete one', cwd=self.repo)
        self.publish()  # establish Students; not force rebuild
        p = publisher.planned_changes(self.config, 'push', base, 'HEAD', self.repo)
        self.assertEqual(p['convert'], ['notebooks/Unit_Tutor.ipynb'])
        self.assertEqual(p['deleted'], ['notebooks/deleted.ipynb'])

    def test_second_publish_same_content_is_noop(self):
        self.publish()
        self.assertEqual(self.publish()['status'], 'unchanged')

    def test_localized_names_and_deletion_preserve_other_language(self):
        self.config['generate_zip'] = False
        self.publish()
        self.other_commit()
        sources = []
        for language in ('fr', 'en'):
            source = f'Course A/Workshop 2/Exercise_Tutor_{language}.ipynb'
            student, archive = publisher.target_names(source, self.config)
            self.assertEqual(student, f'Course A/Workshop 2/Exercise_Student_{language}.ipynb')
            target = self.repo / student
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({'cells': [], 'metadata': {'attached_files': []}}))
            sources.append(source)
        self.plan = {'convert': sources, 'deleted': []}
        self.publish()
        self.plan = {'convert': [], 'deleted': [sources[0]]}
        self.publish()
        git('fetch', 'origin', 'Students', cwd=self.repo)
        paths = git('ls-tree', '-r', '--name-only', 'FETCH_HEAD', cwd=self.repo).splitlines()
        self.assertNotIn('Course A/Workshop 2/Exercise_Student_fr.ipynb', paths)
        self.assertIn('Course A/Workshop 2/Exercise_Student_en.ipynb', paths)
        self.assertIn('slides/course.pdf', paths)

    def test_pdf_publication_preserves_notebook_and_report(self):
        self.publish()
        pdf = self.repo / 'slides/course_fr.pdf'
        pdf.parent.mkdir()
        pdf.write_text('converted animation states')
        publisher.publish_outputs.publish_files({'slides/course_fr.pdf': pdf}, repo=self.repo)
        self.assertEqual(self.remote_file('slides/course_fr.pdf'), 'converted animation states')
        self.assertIn('student', self.remote_file('notebooks/Unit_Student.ipynb'))
        self.assertEqual(self.remote_file('README.md'), '## Student conversion')

    def test_localized_source_without_rename_hook_keeps_converter_name(self):
        self.config['generate_zip'] = False
        generated = self.repo / 'notebooks/Unit_Tutor_fr_Student.ipynb'
        generated.write_text(json.dumps({'cells': [], 'metadata': {}}))
        self.plan = {'convert': ['notebooks/Unit_Tutor_fr.ipynb'], 'deleted': []}
        self.publish()
        self.assertIn('cells', self.remote_file('notebooks/Unit_Tutor_fr_Student.ipynb'))
        self.plan = {'convert': [], 'deleted': ['notebooks/Unit_Tutor_fr.ipynb']}
        self.publish()
        git('fetch', 'origin', 'Students', cwd=self.repo)
        paths = git('ls-tree', '-r', '--name-only', 'FETCH_HEAD', cwd=self.repo).splitlines()
        self.assertNotIn('notebooks/Unit_Tutor_fr_Student.ipynb', paths)

    def test_pdf_retries_without_overwriting_concurrent_notebook(self):
        self.publish()
        pdf = self.repo / 'course.pdf'
        pdf.write_text('new PDF')
        original = publisher.publish_outputs._push
        attempts = []

        def competing(repo, worktree, branch):
            attempts.append('push')
            if len(attempts) == 1:
                self.other_commit('notebooks/Unit_Student.ipynb', 'concurrent notebook')
            return original(repo, worktree, branch)

        with patch.object(publisher.publish_outputs, '_push', side_effect=competing):
            outcome = publisher.publish_outputs.publish_files({'course.pdf': pdf}, repo=self.repo)
        self.assertEqual(outcome['attempts'], 2)
        self.assertEqual(self.remote_file('course.pdf'), 'new PDF')
        self.assertEqual(self.remote_file('notebooks/Unit_Student.ipynb'), 'concurrent notebook')


if __name__ == '__main__':
    unittest.main()
