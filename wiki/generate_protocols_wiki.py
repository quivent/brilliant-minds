#!/usr/bin/env python3
"""
Generate Wikipedia-styled HTML pages for the Brilliant Minds Protocol specifications.
Creates multi-tiered, chunked documentation with proper indexing.

Structure:
    protocols/wiki/
    ├── index.html                      # Main protocols index
    ├── identity-restoration/
    │   ├── index.html                  # Protocol index (links to all sections)
    │   ├── protocol-01-overview.html   # Each ## section is its own page
    │   ├── protocol-02-chunk-prioritization.html
    │   ├── language-guide-01-xxx.html
    │   └── ...
    ├── question-generation/
    │   └── ...
    └── ...
"""

import os
import re
from pathlib import Path
from html import escape

BASE_DIR = Path(__file__).parent
PROTOCOLS_DIR = BASE_DIR / 'protocols'
OUTPUT_DIR = PROTOCOLS_DIR / 'wiki'

PROTOCOLS = {
    'identity_restoration': {
        'name': 'Identity Restoration',
        'slug': 'identity-restoration',
        'description': 'Multi-turn discourse protocol for restoring identities into AI agents.',
        'category': 'Core Pipeline',
        'order': 1,
    },
    'question_generation': {
        'name': 'Question Generation',
        'slug': 'question-generation',
        'description': 'Identity-driven question generation from restored minds.',
        'category': 'Core Pipeline',
        'order': 2,
    },
    'benchmark_selection': {
        'name': 'Benchmark Selection',
        'slug': 'benchmark-selection',
        'description': 'Selection methodology for evaluation benchmarks.',
        'category': 'Core Pipeline',
        'order': 3,
    },
    'repository_evaluation': {
        'name': 'Repository Evaluation',
        'slug': 'repository-evaluation',
        'description': 'Evidence-based repository evaluation and scoring.',
        'category': 'Core Pipeline',
        'order': 4,
    },
    'orchestration': {
        'name': 'Orchestration System',
        'slug': 'orchestration',
        'description': 'System architecture and pipeline coordination.',
        'category': 'System Design',
        'order': 5,
    },
}

FILE_NAMES = {
    'PROTOCOL.md': ('Protocol Specification', 'protocol'),
    'LANGUAGE_GUIDE.md': ('Language Guide', 'language-guide'),
    'SYSTEM.md': ('System Architecture', 'system'),
}

CSS = '''
:root {
    --blue: #3366cc;
    --border: #a2a9b1;
    --bg: #f8f9fa;
    --white: #fff;
    --text: #202122;
    --text-light: #54595d;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14px; line-height: 1.6; color: var(--text); background: var(--bg); }
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }
.header { background: var(--white); border-bottom: 1px solid var(--border); padding: 10px 20px; position: sticky; top: 0; z-index: 100; }
.header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.3em; font-weight: bold; color: var(--text); }
.logo span { color: var(--blue); }
.nav { display: flex; gap: 15px; font-size: 0.9em; }
.main { max-width: 1200px; margin: 0 auto; padding: 20px; }
.content { background: var(--white); border: 1px solid var(--border); border-radius: 2px; padding: 25px 30px; }
.breadcrumb { font-size: 0.85em; color: var(--text-light); margin-bottom: 15px; }
.page-title { font-size: 1.6em; font-weight: normal; font-family: Georgia, serif; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; }
.info-box { background: var(--bg); border: 1px solid var(--border); padding: 15px; margin-bottom: 20px; border-radius: 2px; }
.stats { display: flex; gap: 30px; margin-top: 10px; }
.stat { text-align: center; }
.stat-num { font-size: 1.5em; font-weight: bold; color: var(--blue); }
.stat-label { font-size: 0.8em; color: var(--text-light); }
.section-list { list-style: none; }
.section-item { padding: 12px 15px; border-bottom: 1px solid #eee; }
.section-item:last-child { border-bottom: none; }
.section-item a { font-weight: 500; }
.section-item .meta { font-size: 0.8em; color: var(--text-light); margin-top: 3px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
.card { background: var(--white); border: 1px solid var(--border); padding: 15px; border-radius: 2px; }
.card:hover { box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.card h3 { font-size: 1em; margin-bottom: 5px; }
.card p { font-size: 0.85em; color: var(--text-light); margin-bottom: 8px; }
.card .meta { font-size: 0.75em; color: var(--text-light); }
.doc-list { margin-top: 15px; }
.doc-item { padding: 8px 0; border-bottom: 1px solid #eee; }
.doc-item:last-child { border-bottom: none; }
.category { margin-bottom: 25px; }
.category-title { font-size: 1.1em; font-weight: 600; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid var(--border); }
.page-nav { display: flex; justify-content: space-between; margin-top: 25px; padding-top: 15px; border-top: 1px solid var(--border); font-size: 0.9em; }
.page-nav .prev::before { content: "← "; }
.page-nav .next::after { content: " →"; }
.footer { text-align: center; padding: 20px; color: var(--text-light); font-size: 0.85em; }
/* Content styles */
.wiki-h1 { font-size: 1.3em; font-weight: bold; margin: 25px 0 12px; padding-bottom: 5px; border-bottom: 1px solid var(--border); }
.wiki-h2 { font-size: 1.15em; font-weight: bold; margin: 20px 0 10px; }
.wiki-h3 { font-size: 1.05em; font-weight: bold; margin: 15px 0 8px; }
.wiki-list { margin: 10px 0; padding-left: 25px; }
.wiki-list li { margin-bottom: 5px; }
.wiki-quote { margin: 15px 0; padding: 10px 15px; border-left: 3px solid var(--border); background: var(--bg); font-style: italic; }
.wiki-hr { margin: 20px 0; border: none; border-top: 1px solid var(--border); }
.wiki-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.9em; }
.wiki-table th, .wiki-table td { padding: 8px 10px; border: 1px solid var(--border); text-align: left; }
.wiki-table th { background: var(--bg); font-weight: 600; }
.inline-code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-family: monospace; font-size: 0.9em; color: #d63384; }
.code-block { margin: 15px 0; border: 1px solid var(--border); border-radius: 3px; overflow: hidden; }
.code-header { background: #f1f5f9; padding: 4px 10px; font-size: 0.75em; font-weight: 600; color: var(--text-light); border-bottom: 1px solid var(--border); }
.code-block pre { background: #f8f9fa; padding: 12px; overflow-x: auto; margin: 0; font-family: monospace; font-size: 0.85em; line-height: 1.4; }
p { margin-bottom: 10px; }
/* Index page layout */
.index-layout { display: grid; grid-template-columns: 280px 1fr; gap: 25px; margin-top: 20px; }
.toc-box { background: var(--bg); border: 1px solid var(--border); padding: 15px; border-radius: 2px; height: fit-content; position: sticky; top: 70px; }
.toc-header { font-weight: 600; font-size: 1.1em; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.toc-section { margin-bottom: 15px; }
.toc-title { font-weight: 600; font-size: 0.9em; margin-bottom: 6px; color: var(--text); }
.toc-list { margin: 0; padding-left: 20px; font-size: 0.85em; }
.toc-list li { margin-bottom: 4px; }
.first-section { min-width: 0; }
/* Section page layout */
.section-layout { display: grid; grid-template-columns: 240px 1fr; gap: 25px; }
.section-nav { background: var(--bg); border: 1px solid var(--border); padding: 15px; border-radius: 2px; height: fit-content; position: sticky; top: 70px; font-size: 0.85em; }
.section-toc { margin: 0 0 15px 0; padding-left: 18px; max-height: 60vh; overflow-y: auto; }
.section-toc li { margin-bottom: 6px; line-height: 1.3; }
.section-toc li.current { font-weight: 600; }
.section-toc li.current a { color: var(--text); }
.back-link { display: block; padding-top: 10px; border-top: 1px solid var(--border); font-size: 0.9em; }
.section-content { min-width: 0; }
@media (max-width: 900px) { .index-layout, .section-layout { grid-template-columns: 1fr; } .toc-box, .section-nav { position: static; } }
@media (max-width: 700px) { .card-grid { grid-template-columns: 1fr; } .stats { flex-wrap: wrap; } }
'''


def slugify(text):
    """Convert text to URL-friendly slug."""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'\s+', '-', slug).strip('-')


def parse_sections(md_content):
    """Parse markdown into sections based on ## headings."""
    sections = []
    current_section = None
    current_content = []

    for line in md_content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content)
                })
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
        elif line.startswith('# '):
            # Skip the main title
            continue
        else:
            # Content before first ## goes to intro
            if not sections and not current_section:
                if not any(s.get('title') == '_intro' for s in sections):
                    sections.append({'title': '_intro', 'content': ''})
                if sections:
                    sections[-1]['content'] += line + '\n'

    if current_section:
        sections.append({
            'title': current_section,
            'content': '\n'.join(current_content)
        })

    return sections


def markdown_to_html(md_content):
    """Convert markdown to HTML."""
    code_blocks = []
    def save_code(match):
        idx = len(code_blocks)
        code_blocks.append((match.group(1) or '', match.group(2)))
        return f'__CODE_{idx}__'

    md_content = re.sub(r'```(\w*)\n(.*?)```', save_code, md_content, flags=re.DOTALL)
    html = escape(md_content)

    # Headers
    html = re.sub(r'^####\s+(.+)$', r'<h4 class="wiki-h3">\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3 class="wiki-h3">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2 class="wiki-h2">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1 class="wiki-h1">\1</h1>', html, flags=re.MULTILINE)

    # Inline
    html = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', html)
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Blockquotes
    html = re.sub(r'^&gt;\s+(.+)$', r'<blockquote class="wiki-quote">\1</blockquote>', html, flags=re.MULTILINE)

    # HR
    html = re.sub(r'^---+$', r'<hr class="wiki-hr">', html, flags=re.MULTILINE)

    # Tables
    html = convert_tables(html)

    # Lists
    lines = html.split('\n')
    result = []
    in_list = False
    list_type = None
    for line in lines:
        if re.match(r'^[-*]\s+', line):
            if not in_list:
                result.append('<ul class="wiki-list">')
                in_list, list_type = True, 'ul'
            result.append(f'<li>{re.sub(r"^[-*]\\s+", "", line)}</li>')
        elif re.match(r'^\d+\.\s+', line):
            if not in_list:
                result.append('<ol class="wiki-list">')
                in_list, list_type = True, 'ol'
            result.append(f'<li>{re.sub(r"^\\d+\\.\\s+", "", line)}</li>')
        else:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            result.append(line)
    if in_list:
        result.append(f'</{list_type}>')
    html = '\n'.join(result)

    # Paragraphs
    lines = html.split('\n')
    result = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith('<') and not s.startswith('__CODE_'):
            result.append(f'<p>{line}</p>')
        else:
            result.append(line)
    html = '\n'.join(result)

    # Restore code blocks
    for idx, (lang, code) in enumerate(code_blocks):
        label = lang.upper() if lang else 'CODE'
        html = html.replace(f'__CODE_{idx}__',
            f'<div class="code-block"><div class="code-header">{label}</div><pre><code>{escape(code)}</code></pre></div>')

    return html


def convert_tables(html):
    """Convert markdown tables."""
    lines = html.split('\n')
    result = []
    in_table = False
    rows = []

    for line in lines:
        s = line.strip()
        if '|' in s and s.startswith('|'):
            if re.match(r'^\|[\s\-:|]+\|$', s):
                continue
            if not in_table:
                in_table = True
                rows = []
            rows.append([c.strip() for c in s.split('|')[1:-1]])
        else:
            if in_table:
                result.append(render_table(rows))
                in_table = False
                rows = []
            result.append(line)
    if in_table:
        result.append(render_table(rows))
    return '\n'.join(result)


def render_table(rows):
    if not rows:
        return ''
    html = '<table class="wiki-table"><thead><tr>'
    for c in rows[0]:
        html += f'<th>{c}</th>'
    html += '</tr></thead>'
    if len(rows) > 1:
        html += '<tbody>'
        for row in rows[1:]:
            html += '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
        html += '</tbody>'
    return html + '</table>'


def page_template(title, breadcrumbs, content, nav_prev=None, nav_next=None, depth=0):
    """Generate HTML page."""
    prefix = '../' * depth
    bc_html = ' &gt; '.join(f'<a href="{prefix}{url}">{name}</a>' if url else name for name, url in breadcrumbs)

    nav_html = ''
    if nav_prev or nav_next:
        prev_link = f'<a href="{nav_prev[1]}" class="prev">{nav_prev[0]}</a>' if nav_prev else '<span></span>'
        next_link = f'<a href="{nav_next[1]}" class="next">{nav_next[0]}</a>' if nav_next else '<span></span>'
        nav_html = f'<nav class="page-nav">{prev_link}{next_link}</nav>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Brilliant Minds Protocols</title>
<style>{CSS}</style>
</head>
<body>
<header class="header">
<div class="header-content">
<a href="{prefix}index.html" class="logo">Brilliant<span>Minds</span> Protocols</a>
<nav class="nav">
<a href="{prefix}index.html">Index</a>
<a href="{prefix}../index.html">Minds Corpus</a>
</nav>
</div>
</header>
<main class="main">
<div class="content">
<div class="breadcrumb">{bc_html}</div>
<h1 class="page-title">{title}</h1>
{content}
{nav_html}
</div>
</main>
<footer class="footer">Brilliant Minds Protocol Documentation</footer>
</body>
</html>'''


def generate_main_index(protocols_data):
    """Generate main index.html."""
    categories = {}
    for pid, data in protocols_data.items():
        cat = PROTOCOLS[pid]['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(data)

    for cat in categories:
        categories[cat].sort(key=lambda x: PROTOCOLS[x['id']]['order'])

    content = '''<div class="info-box">
<p>Technical specifications for the Brilliant Minds evaluation system.</p>
<div class="stats">
<div class="stat"><div class="stat-num">5</div><div class="stat-label">Protocols</div></div>
<div class="stat"><div class="stat-num">6</div><div class="stat-label">Documents</div></div>
<div class="stat"><div class="stat-num">{}</div><div class="stat-label">Sections</div></div>
</div>
</div>'''.format(sum(d['total_sections'] for d in protocols_data.values()))

    for cat_name, protos in categories.items():
        cards = ''
        for p in protos:
            docs = ''.join(f'<div class="doc-item"><a href="{p["slug"]}/{d["slug"]}-01.html">{d["name"]}</a> <span style="color:#666">({len(d["sections"])} sections)</span></div>'
                          for d in p['documents'])
            cards += f'''<div class="card">
<h3><a href="{p['slug']}/index.html">{p['name']}</a></h3>
<p>{p['description']}</p>
<div class="doc-list">{docs}</div>
</div>'''
        content += f'<div class="category"><h2 class="category-title">{cat_name}</h2><div class="card-grid">{cards}</div></div>'

    return page_template('Protocol Specifications', [('Protocols', None)], content)


def generate_protocol_index(protocol_id, data):
    """Generate protocol index page with first section content displayed."""
    info = PROTOCOLS[protocol_id]

    # Build compact TOC for sidebar
    toc_html = ''
    first_section = None
    first_section_doc = None

    for doc in data['documents']:
        valid_sections = [(i, s) for i, s in enumerate(doc['sections']) if s['title'] != '_intro']
        if valid_sections and not first_section:
            first_section = valid_sections[0][1]
            first_section_doc = doc

        items = ''.join(
            f'<li><a href="{doc["slug"]}-{i+1:02d}.html">{s["title"]}</a></li>'
            for i, s in valid_sections
        )
        toc_html += f'''<div class="toc-section">
<div class="toc-title">{doc['name']}</div>
<ol class="toc-list">{items}</ol>
</div>'''

    # Render first section content
    first_content = ''
    nav_next = None
    if first_section:
        first_content = markdown_to_html(first_section['content'])
        # Find next section for navigation
        valid = [(i, s) for i, s in enumerate(first_section_doc['sections']) if s['title'] != '_intro']
        if len(valid) > 1:
            nav_next = (valid[1][1]['title'], f'{first_section_doc["slug"]}-02.html')

    content = f'''<div class="info-box">
<p>{info['description']}</p>
<div class="stats">
<div class="stat"><div class="stat-num">{len(data['documents'])}</div><div class="stat-label">Documents</div></div>
<div class="stat"><div class="stat-num">{data['total_sections']}</div><div class="stat-label">Sections</div></div>
</div>
</div>
<div class="index-layout">
<div class="toc-box">
<div class="toc-header">Contents</div>
{toc_html}
</div>
<div class="first-section">
<h2 class="wiki-h2">{first_section['title'] if first_section else 'Overview'}</h2>
{first_content}
</div>
</div>'''

    return page_template(info['name'], [('Protocols', 'index.html'), (info['name'], None)], content, nav_next=nav_next, depth=1)


def generate_section_page(protocol_id, doc_info, section_idx, sections, doc_slug):
    """Generate individual section page with section navigation sidebar."""
    info = PROTOCOLS[protocol_id]
    section = sections[section_idx]

    # Skip intro sections
    if section['title'] == '_intro':
        return None

    # Build section navigation sidebar
    valid_sections = [(i, s) for i, s in enumerate(sections) if s['title'] != '_intro']
    current_num = sum(1 for i, s in valid_sections if i < section_idx) + 1

    toc_items = ''
    for i, s in valid_sections:
        page_num = sum(1 for j, _ in valid_sections if j <= i)
        is_current = (i == section_idx)
        cls = ' class="current"' if is_current else ''
        toc_items += f'<li{cls}><a href="{doc_slug}-{page_num:02d}.html">{s["title"]}</a></li>'

    # Find prev/next
    nav_prev = nav_next = None
    if section_idx > 0:
        prev_s = sections[section_idx - 1]
        if prev_s['title'] != '_intro':
            nav_prev = (prev_s['title'], f'{doc_slug}-{section_idx:02d}.html')
    if section_idx < len(sections) - 1:
        next_s = sections[section_idx + 1]
        nav_next = (next_s['title'], f'{doc_slug}-{section_idx + 2:02d}.html')

    content_html = markdown_to_html(section['content'])
    lines = len(section['content'].split('\n'))

    content = f'''<div class="section-layout">
<div class="section-nav">
<div class="toc-header">{doc_info[0]}</div>
<ol class="section-toc">{toc_items}</ol>
<a href="index.html" class="back-link">← Back to Overview</a>
</div>
<div class="section-content">
<div class="info-box">
<p>Section {current_num} of {len(valid_sections)} &middot; {lines} lines</p>
</div>
{content_html}
</div>
</div>'''

    breadcrumbs = [
        ('Protocols', '../index.html'),
        (info['name'], 'index.html'),
        (section['title'], None)
    ]

    return page_template(section['title'], breadcrumbs, content, nav_prev, nav_next, depth=1)


def main():
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process all protocols
    protocols_data = {}

    for protocol_id, info in PROTOCOLS.items():
        protocol_path = PROTOCOLS_DIR / protocol_id
        if not protocol_path.exists():
            continue

        slug = info['slug']
        proto_output = OUTPUT_DIR / slug
        proto_output.mkdir(exist_ok=True)

        data = {
            'id': protocol_id,
            'name': info['name'],
            'slug': slug,
            'description': info['description'],
            'documents': [],
            'total_sections': 0
        }

        # Process each document
        for md_file in sorted(protocol_path.glob('*.md')):
            if md_file.name not in FILE_NAMES:
                continue

            doc_name, doc_slug = FILE_NAMES[md_file.name]
            content = md_file.read_text(encoding='utf-8')
            sections = parse_sections(content)

            # Filter out empty intro sections
            sections = [s for s in sections if s['content'].strip() or s['title'] != '_intro']

            doc_data = {
                'name': doc_name,
                'slug': doc_slug,
                'sections': sections
            }
            data['documents'].append(doc_data)
            data['total_sections'] += len([s for s in sections if s['title'] != '_intro'])

            # Generate section pages
            section_num = 0
            for i, section in enumerate(sections):
                if section['title'] == '_intro':
                    continue
                section_num += 1
                page_html = generate_section_page(protocol_id, (doc_name, doc_slug), i, sections, doc_slug)
                if page_html:
                    page_path = proto_output / f'{doc_slug}-{section_num:02d}.html'
                    page_path.write_text(page_html, encoding='utf-8')
                    print(f'  {page_path.name} ({page_path.stat().st_size // 1024} KB)')

        # Generate protocol index
        index_html = generate_protocol_index(protocol_id, data)
        index_path = proto_output / 'index.html'
        index_path.write_text(index_html, encoding='utf-8')
        print(f'{slug}/index.html')

        protocols_data[protocol_id] = data

    # Generate main index
    main_index = generate_main_index(protocols_data)
    main_path = OUTPUT_DIR / 'index.html'
    main_path.write_text(main_index, encoding='utf-8')
    print(f'\nindex.html')

    # Summary
    total_pages = 1 + len(protocols_data)  # main index + protocol indexes
    for d in protocols_data.values():
        total_pages += d['total_sections']

    print(f'\n✓ Generated {total_pages} pages in protocols/wiki/')


if __name__ == '__main__':
    main()
