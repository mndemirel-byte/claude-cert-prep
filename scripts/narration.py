import re

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
