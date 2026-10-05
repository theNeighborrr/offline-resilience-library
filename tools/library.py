"""Build and package a serverless offline library. Python 3.10+, no dependencies."""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE_FILES = ('START-HERE.html', 'assets/style.css', 'assets/app.js', 'catalog.json')
SOURCE_FILES = ('README.md', '.gitignore', '.gitattributes', 'docs/ROADMAP.md', 'templates/start.html',
                'tools/library.py', 'tests/test_library.py', 'tests/test_search.js')


def safe_path(root: Path, relative: str) -> Path:
    """Reject traversal, Windows drive paths, and links escaping the library."""
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise ValueError(f'Invalid relative path: {relative!r}')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or relative != rel.as_posix():
        raise ValueError(f'Unsafe path: {relative}')
    destination = (root / relative).resolve()
    if not destination.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes library: {relative}')
    return destination


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def read_catalog(root: Path) -> dict:
    catalog = json.loads((root / 'catalog.json').read_text(encoding='utf-8'))
    if not re.fullmatch(r'\d+\.\d+\.\d+', catalog['version']):
        raise ValueError('Version must have the form 0.1.0')
    categories = {c['id'] for c in catalog['categories']}
    if len(categories) != len(catalog['categories']):
        raise ValueError('Duplicate category')
    identifiers = set()
    for item in catalog['items']:
        if not re.fullmatch(r'[a-z0-9-]+', item['id']) or item['id'] in identifiers:
            raise ValueError('Invalid or duplicate item ID')
        identifiers.add(item['id'])
        if item['category'] not in categories:
            raise ValueError(f'Unknown category: {item["category"]}')
        if item['state'] not in ('included', 'planned'):
            raise ValueError('Invalid item state')
        source = item.get('source_url')
        if source and (urlsplit(source).scheme != 'https' or not urlsplit(source).hostname):
            raise ValueError('Source links must use HTTPS')
        if item['state'] == 'included':
            path = safe_path(root, item['path'])
            if not item['path'].startswith('content/') or not path.is_file():
                raise ValueError(f'Included file missing or outside content/: {item["path"]}')
            if item['rights_status'] not in ('original', 'reviewed') or not item.get('rights_note'):
                raise ValueError('Included content requires a rights record')
            if not item.get('attribution') or not item.get('reader'):
                raise ValueError('Included content requires attribution and a reader description')
            expected = item.get('sha256')
            if item['rights_status'] != 'original' and not expected:
                raise ValueError('Third-party content requires a recorded SHA-256')
            if expected and digest(path) != expected:
                raise ValueError(f'Content hash mismatch: {item["path"]}')
        elif item.get('path'):
            raise ValueError('Planned entries must not have a local path')
    return catalog


def portable_files(catalog: dict) -> list[str]:
    return sorted(set(BASE_FILES) | {i['path'] for i in catalog['items'] if i['state'] == 'included'})


def render(root: Path, catalog: dict) -> str:
    escape = html.escape
    categories = {c['id']: c['label'] for c in catalog['categories']}
    topics = '<li><button type="button" data-topic="all" aria-pressed="true">All topics</button></li>'
    for cat in catalog['categories']:
        topics += f'<li><button type="button" data-topic="{escape(cat["id"])}" aria-pressed="false">{escape(cat["number"])} &nbsp; {escape(cat["label"])}</button></li>'
    cards = []
    for item in catalog['items']:
        included = item['state'] == 'included'
        label = 'Included offline' if included else 'To add'
        badge_class = '' if included else ' planned'
        search = ' '.join((item['title'], item['description'], item['keywords'], categories[item['category']])).lower()
        if included:
            action = f'<a href="{escape(item["path"])}">Open included page →</a>'
        else:
            action = f'<a href="{escape(item["source_url"])}" target="_blank" rel="noopener noreferrer">View source · internet required ↗</a>' if item.get('source_url') else '<span>Source selection pending</span>'
        cards.append(f'''<article class="card" data-category="{escape(item['category'])}" data-state="{item['state']}" data-search="{escape(search)}">
<div class="card-meta"><span>{escape(categories[item['category']])}</span><span class="badge{badge_class}">{label}</span></div>
<h2>{escape(item['title'])}</h2><p>{escape(item['description'])}</p>
<p class="reader">{escape(item['reader'])}</p><div class="card-actions">{action}</div>
<details><summary>Source &amp; edition notes</summary><p>{escape(item['publisher'])} · {escape(item.get('edition') or 'Edition not selected')}</p><p>{escape(item['rights_note'])}</p></details></article>''')
    included_count = sum(i['state'] == 'included' for i in catalog['items'])
    values = {'VERSION': catalog['version'], 'DATE': catalog['edition_date'], 'TOPICS': topics,
              'CARDS': '\n'.join(cards), 'INCLUDED': str(included_count),
              'PLANNED': str(len(cards) - included_count), 'TOTAL': str(len(cards))}
    output = (root / 'templates/start.html').read_text(encoding='utf-8')
    for key, value in values.items():
        output = output.replace('{{' + key + '}}', value)
    if re.search(r'\{\{[A-Z]+\}\}', output):
        raise ValueError('Unexpanded template field')
    return output


class LinkCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append((tag, attrs[key]))


def check_links(root: Path, files: list[str]) -> None:
    allowed = set(files)
    for name in files:
        if not name.endswith('.html'):
            continue
        parser = LinkCheck()
        parser.feed(safe_path(root, name).read_text(encoding='utf-8'))
        for tag, link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                if tag != 'a' or parsed.scheme != 'https':
                    raise ValueError(f'External dependency or unsafe URL: {name}: {link}')
                continue
            if not parsed.path:
                continue
            target = (safe_path(root, name).parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(root.resolve()):
                raise ValueError(f'Link escapes library: {name}: {link}')
            relative = target.relative_to(root.resolve()).as_posix()
            if relative not in allowed or not target.is_file():
                raise ValueError(f'Link target is not packaged: {name}: {link}')


def build(root: Path) -> dict:
    catalog = read_catalog(root)
    (root / 'START-HERE.html').write_text(render(root, catalog), encoding='utf-8', newline='\n')
    files = portable_files(catalog)
    check_links(root, files)
    manifest = {'version': catalog['version'], 'files': {name: {'sha256': digest(safe_path(root, name)),
                'bytes': safe_path(root, name).stat().st_size} for name in files}}
    (root / 'SHA256SUMS.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def verify(root: Path) -> dict:
    catalog = read_catalog(root)
    manifest = json.loads((root / 'SHA256SUMS.json').read_text(encoding='utf-8'))
    files = portable_files(catalog)
    if manifest['version'] != catalog['version'] or set(manifest['files']) != set(files):
        raise ValueError('Manifest/catalog mismatch; rebuild before packaging')
    for name in files:
        path = safe_path(root, name)
        expected = manifest['files'][name]
        if not path.is_file() or path.stat().st_size != expected['bytes'] or digest(path) != expected['sha256']:
            raise ValueError(f'File missing or changed: {name}')
    # The portable archive does not need the authoring template.
    if (root / 'templates/start.html').is_file() and (root / 'START-HERE.html').read_text(encoding='utf-8') != render(root, catalog):
        raise ValueError('Homepage is stale; rebuild after template edits')
    check_links(root, files)
    return manifest


def package(root: Path) -> list[Path]:
    manifest = verify(root)
    version = manifest['version']
    destination = root / 'dist'
    destination.mkdir(exist_ok=True)
    prefix = f'Offline-Resilience-Library-{version}'
    portable = sorted(set(manifest['files']) | {'SHA256SUMS.json'})
    source = sorted(set(portable) | set(SOURCE_FILES))
    # Bulk third-party content stays out of the source ZIP; the portable ZIP has
    # only explicitly cataloged files. v0.1 contains original HTML pages only.
    source = [name for name in source if not name.startswith('content/external/')]
    targets = [(destination / f'{prefix}-Portable.zip', portable),
               (destination / f'{prefix}-Source.zip', source)]
    if any(target.exists() for target, _ in targets):
        raise ValueError('A release ZIP already exists; choose a new version or move the old ZIPs')
    for _, names in targets:
        for name in names:
            if not safe_path(root, name).is_file():
                raise ValueError(f'Package file missing: {name}')
    for target, names in targets:
        with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for name in names:
                archive.write(safe_path(root, name), f'{prefix}/{name}')
    return [target for target, _ in targets]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'verify', 'package'))
    parser.add_argument('--root', type=Path, default=ROOT, help='Library root; useful for checking a copied drive')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'package':
            for output in package(root):
                print(output)
        else:
            result = build(root) if args.command == 'build' else verify(root)
            print(f'{args.command}: OK; {len(result["files"])} files; version {result["version"]}')
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
