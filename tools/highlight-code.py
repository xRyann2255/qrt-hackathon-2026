#!/usr/bin/env python3
# Write docs/code/q1..q5.html, the "Show code" panes: each submitted solution, unchanged, highlighted by Pygments.
# Pygments only adds token classes and one span per line (numbered by CSS); the colours are in docs/style.css.
# Rerun after a solution changes.
from pathlib import Path
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename

root = Path(__file__).resolve().parent.parent
out = root / 'docs/code'
out.mkdir(exist_ok=True)
for src in sorted(root.glob('solutions/q*/solution.*')):
    lexer = get_lexer_for_filename(src.name, stripnl=False)
    html = highlight(src.read_text(encoding='utf-8'), lexer, HtmlFormatter(linespans='L'))
    (out / f'{src.parent.name}.html').write_text(html, encoding='utf-8')
    print(src.relative_to(root), f'{len(html) // 1024} KB')
