#!/usr/bin/env python3
# Write docs/code/q1..q5.html, the "Show code" panes: each submitted solution, unchanged, highlighted by Pygments.
# Pygments only adds token classes and one span per line (numbered by CSS); the colours are in docs/style.css.
# tools/notes/qN.json, if present, splits the file into chunks ([{"lines": [a, b], "title", "text"}], in order):
# each chunk's lines get data-c, its first line is focusable, and the notes go in a panel beside the code.
# Rerun after a solution or its notes change.
import json
from html import escape
from pathlib import Path
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename

root = Path(__file__).resolve().parent.parent
out = root / 'docs/code'
out.mkdir(exist_ok=True)
for src in sorted(root.glob('solutions/q*/solution.*')):
    q, code = src.parent.name, src.read_text(encoding='utf-8')
    html = highlight(code, get_lexer_for_filename(src.name, stripnl=False), HtmlFormatter(linespans='L'))
    notes = root / f'tools/notes/{q}.json'
    if notes.exists():
        panel, end = ['<div data-c="-1" class="on"><b><span class="mouse">Hover over</span><span class="touch">Tap</span> a block of code'
                      ' to see what it does</b><p>A faint line at the left edge marks each block. With a keyboard, tab into'
                      ' the code.</p></div>'], 0
        for i, c in enumerate(json.loads(notes.read_text(encoding='utf-8'))):
            a, b = c['lines']
            assert end < a <= b <= code.count('\n') + 1, f'{notes}: chunk {i} lines {a}-{b} overlap or out of range'
            end = b
            for n in range(a, b + 1):
                attrs = f' data-c="{i}"' + (f' tabindex="0" aria-describedby="note-{i}"' if n == a else '')
                html = html.replace(f'<span id="L-{n}">', f'<span id="L-{n}"{attrs}>', 1)
            where = f'line {a}' if a == b else f'lines {a} to {b}'
            panel.append(f'<div data-c="{i}" id="note-{i}"><b>{escape(c["title"])}</b> <small>{where}</small>'
                         f'<p>{escape(c["text"])}</p></div>')
        html = f'<div class="annotated">{html}<aside class="notes">{"".join(panel)}</aside></div>\n'
    (out / f'{q}.html').write_text(html, encoding='utf-8')
    print(src.relative_to(root), f'{len(html) // 1024} KB', 'with notes' if notes.exists() else '')
