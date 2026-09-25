import hashlib
import os
import re
from dataclasses import dataclass
from typing import Optional

HEADING_RE = re.compile(r'^#{1,6}\s+(.*)$', re.M)
CODE_FENCE_RE = re.compile(r'```.*?```', re.S)
BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
ITALIC_RE = re.compile(r'\*(.+?)\*')
LINK_RE = re.compile(r'\[(.+?)\]\(.+?\)')
TABLE_BLOCK_RE = re.compile(r'(?:^\|.*\|\s*$\n?)+', re.M)


def _flatten_table_block(match: re.Match) -> str:
    rows = []
    for line in match.group(0).splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r'-+', c) for c in cells):
            continue
        rows.append(', '.join(cells) + '.')
    return ' '.join(rows)


def prepare_narration_text(markdown: str) -> str:
    text = CODE_FENCE_RE.sub("Here's a code example.", markdown)
    text = HEADING_RE.sub(r'\1', text)
    text = LINK_RE.sub(r'\1', text)
    text = BOLD_RE.sub(r'\1', text)
    text = ITALIC_RE.sub(r'\1', text)
    text = TABLE_BLOCK_RE.sub(_flatten_table_block, text)
    return text


@dataclass
class LessonSource:
    id: str
    domain: int
    en_path: Optional[str]
    tr_path: Optional[str]


EN_LESSON_FILENAME_RE = re.compile(r'^(\d+)\.(\d+)\.md$')
TR_LESSON_FILENAME_RE = re.compile(r'^task_statement_(\d+)_(\d+)_.*?(_TR)?\.md$')


def discover_lessons(en_dir: str, tr_dir: str) -> list:
    sources = {}

    for name in sorted(os.listdir(en_dir)):
        m = EN_LESSON_FILENAME_RE.match(name)
        if not m:
            continue
        domain, n = int(m.group(1)), int(m.group(2))
        lesson_id = f"{domain}.{n}"
        sources.setdefault(lesson_id, LessonSource(lesson_id, domain, None, None))
        sources[lesson_id].en_path = os.path.join(en_dir, name)

    for name in sorted(os.listdir(tr_dir)):
        if 'practice_exam' in name or 'yeterlilik_testi' in name:
            continue
        m = TR_LESSON_FILENAME_RE.match(name)
        if not m or not m.group(3):
            continue
        domain, n = int(m.group(1)), int(m.group(2))
        lesson_id = f"{domain}.{n}"
        sources.setdefault(lesson_id, LessonSource(lesson_id, domain, None, None))
        sources[lesson_id].tr_path = os.path.join(tr_dir, name)

    return [sources[k] for k in sorted(sources, key=lambda k: tuple(map(int, k.split('.'))))]


@dataclass
class NarrationJob:
    id: str
    language: str
    text: str


def split_into_chunks(text: str, max_chars: int) -> list:
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""
    for paragraph in text.split('\n\n'):
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def narration_filename(lesson_id: str) -> str:
    domain, n = lesson_id.split('.')
    return f"D{domain}-{n}.mp3"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def plan_narration_jobs(lesson_texts: dict, manifest: dict) -> list:
    jobs = []
    for (lesson_id, language), text in lesson_texts.items():
        key = f"{lesson_id}:{language}"
        if manifest.get(key) != content_hash(text):
            jobs.append(NarrationJob(id=lesson_id, language=language, text=text))
    return jobs
