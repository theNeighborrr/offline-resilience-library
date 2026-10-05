import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('library', ROOT / 'tools/library.py')
library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'library'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__', 'private', 'downloads'))
        library.build(self.root)

    def edit_catalog(self, edit):
        path = self.root / 'catalog.json'
        catalog = json.loads(path.read_text(encoding='utf-8'))
        edit(catalog)
        path.write_text(json.dumps(catalog), encoding='utf-8')

    def test_copy_is_self_contained_and_private_files_are_excluded(self):
        secret = self.root / 'private' / 'contacts.txt'
        secret.parent.mkdir()
        secret.write_text('private test fixture')
        portable, source = library.package(self.root)
        with zipfile.ZipFile(portable) as archive:
            self.assertFalse(any('private' in n for n in archive.namelist()))
            destination = Path(self.temp.name) / 'usb-copy'
            archive.extractall(destination)
        copied = next(destination.iterdir())
        self.assertEqual(len(library.verify(copied)['files']), 8)
        with zipfile.ZipFile(source) as archive:
            self.assertFalse(any('private' in n or '/.git/' in n for n in archive.namelist()))

    def test_changed_copy_fails_verification(self):
        with (self.root / 'content/guides/inventory.html').open('a', encoding='utf-8') as stream:
            stream.write('changed')
        with self.assertRaisesRegex(ValueError, 'changed'):
            library.verify(self.root)

    def test_path_traversal_is_rejected(self):
        for path in ('../outside.txt', 'content/../../outside.txt', 'C:/outside.txt', '/outside.txt', 'content\\outside.txt'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                library.safe_path(self.root, path)

    def test_planned_item_cannot_claim_local_content(self):
        self.edit_catalog(lambda c: c['items'][4].update(path='content/guides/inventory.html'))
        with self.assertRaisesRegex(ValueError, 'Planned'):
            library.build(self.root)

    def test_third_party_content_requires_recorded_checksum(self):
        self.edit_catalog(lambda c: c['items'][0].update(rights_status='reviewed', sha256=None))
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            library.build(self.root)

    def test_remote_dependency_fails_build(self):
        with (self.root / 'templates/start.html').open('a', encoding='utf-8') as stream:
            stream.write('<script src="https://example.org/tracker.js"></script>')
        with self.assertRaisesRegex(ValueError, 'External dependency'):
            library.build(self.root)

    def test_missing_local_link_fails_build(self):
        with (self.root / 'content/guides/inventory.html').open('a', encoding='utf-8') as stream:
            stream.write('<a href="missing.pdf">Missing</a>')
        with self.assertRaisesRegex(ValueError, 'not packaged'):
            library.build(self.root)

    def test_stale_template_fails_packaging(self):
        with (self.root / 'templates/start.html').open('a', encoding='utf-8') as stream:
            stream.write('\n<!-- changed -->')
        with self.assertRaisesRegex(ValueError, 'stale'):
            library.package(self.root)

    def test_package_does_not_replace_existing_release(self):
        targets = library.package(self.root)
        original = [library.digest(p) for p in targets]
        with self.assertRaisesRegex(ValueError, 'already exists'):
            library.package(self.root)
        self.assertEqual(original, [library.digest(p) for p in targets])


if __name__ == '__main__':
    unittest.main()

