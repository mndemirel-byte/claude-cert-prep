import re

TAKEAWAYS_HEADING_RE = re.compile(
    r'^##\s+(?:Key Exam Takeaways|Key Takeaways|Sınav İçin Temel Çıkarımlar|Key Takeaway Listesi)\s*$',
    re.M,
)


def extract_flashcards(markdown: str) -> list:
    m = TAKEAWAYS_HEADING_RE.search(markdown)
    if not m:
        return []
    rest = markdown[m.end():]
    end_m = re.search(r'^(#{1,6}\s|---\s*$)', rest, re.M)
    section = rest[:end_m.start()] if end_m else rest
    lines = [l for l in section.strip().splitlines() if l.strip().startswith('|')]
    cards = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        cards.append({"concept": cells[0], "remember": cells[1]})
    return cards
