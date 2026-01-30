#!/usr/bin/env python3
"""
Generate a Wikipedia-styled HTML page for the Brilliant Minds corpus.
"""

import os
import re
from pathlib import Path
from html import escape

# Directory containing all the brilliant minds
BASE_DIR = Path(__file__).parent

# Display names for each person
DISPLAY_NAMES = {
    'alan_turing': 'Alan Turing',
    'albert_einstein': 'Albert Einstein',
    'andrej_karpathy': 'Andrej Karpathy',
    'andrew_ng': 'Andrew Ng',
    'bjarne_stroustrup': 'Bjarne Stroustrup',
    'dave_ferrucci': 'Dave Ferrucci',
    'demis_hassabis': 'Demis Hassabis',
    'dennis_ritchie': 'Dennis Ritchie',
    'donald_knuth': 'Donald Knuth',
    'edward_hu': 'Edward Hu',
    'elon_musk': 'Elon Musk',
    'fei_fei_li': 'Fei-Fei Li',
    'geoffrey_hinton': 'Geoffrey Hinton',
    'grace_hopper': 'Grace Hopper',
    'guido_van_rossum': 'Guido van Rossum',
    'ilya_sutskever': 'Ilya Sutskever',
    'james_gosling': 'James Gosling',
    'jeff_dean': 'Jeff Dean',
    'jensen_huang': 'Jensen Huang',
    'john_carmack': 'John Carmack',
    'john_mccarthy': 'John McCarthy',
    'linus_torvalds': 'Linus Torvalds',
    'steve_jobs': 'Steve Jobs',
    'yann_lecun': 'Yann LeCun',
    'yoshua_bengio': 'Yoshua Bengio',
}

# Categories for organization
CATEGORIES = {
    'AI Pioneers & Deep Learning': [
        'geoffrey_hinton', 'yann_lecun', 'yoshua_bengio', 'john_mccarthy'
    ],
    'AI Industry Leaders': [
        'jeff_dean', 'ilya_sutskever', 'andrej_karpathy', 'andrew_ng',
        'fei_fei_li', 'demis_hassabis', 'dave_ferrucci', 'edward_hu'
    ],
    'Programming Language Creators': [
        'dennis_ritchie', 'james_gosling', 'bjarne_stroustrup', 'guido_van_rossum'
    ],
    'Systems & Hardware Innovators': [
        'linus_torvalds', 'jensen_huang', 'john_carmack'
    ],
    'Visionary Founders': [
        'steve_jobs', 'elon_musk'
    ],
    'Historical Giants': [
        'albert_einstein', 'alan_turing', 'donald_knuth', 'grace_hopper'
    ],
}

def markdown_to_html(md_content):
    """Convert markdown to HTML with basic formatting."""
    html = escape(md_content)

    # Convert headers
    html = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3 class="wiki-h3">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2 class="wiki-h2">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1 class="wiki-h1">\1</h1>', html, flags=re.MULTILINE)

    # Convert bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="wiki-link">\1</a>', html)

    # Convert blockquotes
    html = re.sub(r'^&gt;\s+(.+)$', r'<blockquote class="wiki-quote">\1</blockquote>', html, flags=re.MULTILINE)

    # Convert horizontal rules
    html = re.sub(r'^---+$', r'<hr class="wiki-hr">', html, flags=re.MULTILINE)

    # Convert unordered lists
    lines = html.split('\n')
    in_list = False
    result = []
    for line in lines:
        if re.match(r'^[-*]\s+', line):
            if not in_list:
                result.append('<ul class="wiki-list">')
                in_list = True
            content = re.sub(r'^[-*]\s+', '', line)
            result.append(f'<li>{content}</li>')
        elif re.match(r'^\d+\.\s+', line):
            if not in_list:
                result.append('<ol class="wiki-list">')
                in_list = True
            content = re.sub(r'^\d+\.\s+', '', line)
            result.append(f'<li>{content}</li>')
        else:
            if in_list:
                if result[-1].startswith('<ol'):
                    result.append('</ol>')
                else:
                    result.append('</ul>')
                in_list = False
            result.append(line)

    if in_list:
        result.append('</ul>')

    html = '\n'.join(result)

    # Convert paragraphs (lines with content that aren't already tags)
    lines = html.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<') and not stripped.startswith('</'):
            result.append(f'<p>{line}</p>')
        else:
            result.append(line)

    return '\n'.join(result)

def get_person_content(person_dir):
    """Get all markdown content for a person."""
    content = {}
    person_path = BASE_DIR / person_dir

    if not person_path.exists():
        return content

    # Get all markdown files, sorted
    md_files = sorted(person_path.glob('*.md'))

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content[md_file.name] = f.read()

    return content

def generate_toc_entry(person_id, display_name, files):
    """Generate table of contents entry for a person."""
    file_links = []
    for filename in sorted(files.keys()):
        nice_name = filename.replace('.md', '').replace('_', ' ').title()
        if nice_name == 'Identity':
            nice_name = 'Identity Document'
        file_links.append(f'<a href="#{person_id}-{filename.replace(".md", "")}">{nice_name}</a>')

    return f'''
    <li class="toc-person">
        <a href="#{person_id}" class="toc-person-link">{display_name}</a>
        <ul class="toc-files">
            {''.join(f"<li>{link}</li>" for link in file_links)}
        </ul>
    </li>
    '''

def generate_person_section(person_id, display_name, files):
    """Generate the full section for a person."""
    sections = []

    for filename in sorted(files.keys()):
        file_id = f"{person_id}-{filename.replace('.md', '')}"
        nice_name = filename.replace('.md', '').replace('_', ' ').title()
        if nice_name == 'Identity':
            nice_name = 'Identity Document'

        html_content = markdown_to_html(files[filename])

        sections.append(f'''
        <div class="document-section" id="{file_id}">
            <div class="document-header">
                <span class="document-type">{nice_name}</span>
            </div>
            <div class="document-content">
                {html_content}
            </div>
        </div>
        ''')

    return f'''
    <article class="person-article" id="{person_id}">
        <header class="person-header">
            <h1 class="person-name">{display_name}</h1>
            <div class="person-meta">
                <span class="doc-count">{len(files)} documents</span>
            </div>
        </header>
        <div class="person-content">
            {''.join(sections)}
        </div>
        <div class="back-to-top">
            <a href="#top">Back to top</a>
        </div>
    </article>
    '''

def generate_html():
    """Generate the complete HTML page."""

    # Collect all content
    all_people = {}
    for person_id in DISPLAY_NAMES.keys():
        content = get_person_content(person_id)
        if content:
            all_people[person_id] = content

    # Generate TOC by category
    toc_sections = []
    for category, people in CATEGORIES.items():
        category_entries = []
        for person_id in people:
            if person_id in all_people:
                entry = generate_toc_entry(person_id, DISPLAY_NAMES[person_id], all_people[person_id])
                category_entries.append(entry)

        if category_entries:
            toc_sections.append(f'''
            <div class="toc-category">
                <h3 class="toc-category-title">{category}</h3>
                <ul class="toc-list">
                    {''.join(category_entries)}
                </ul>
            </div>
            ''')

    # Generate person sections
    person_sections = []
    for category, people in CATEGORIES.items():
        category_people = []
        for person_id in people:
            if person_id in all_people:
                section = generate_person_section(person_id, DISPLAY_NAMES[person_id], all_people[person_id])
                category_people.append(section)

        if category_people:
            person_sections.append(f'''
            <section class="category-section">
                <h2 class="category-title" id="cat-{category.lower().replace(' ', '-').replace('&', 'and')}">{category}</h2>
                {''.join(category_people)}
            </section>
            ''')

    # Complete HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brilliant Minds Corpus - Wikipedia Style Documentation</title>
    <style>
        /* Wikipedia-inspired styling */
        :root {{
            --wiki-blue: #3366cc;
            --wiki-blue-hover: #447ff5;
            --wiki-red: #ba0000;
            --wiki-border: #a2a9b1;
            --wiki-background: #f8f9fa;
            --wiki-content-bg: #ffffff;
            --wiki-text: #202122;
            --wiki-text-light: #54595d;
            --wiki-header-border: #a2a9b1;
            --wiki-infobox-bg: #f8f9fa;
            --wiki-toc-bg: #f8f9fa;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Liberation Sans', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: var(--wiki-text);
            background-color: var(--wiki-background);
        }}

        /* Header */
        .wiki-header {{
            background: var(--wiki-content-bg);
            border-bottom: 1px solid var(--wiki-border);
            padding: 10px 20px;
            position: sticky;
            top: 0;
            z-index: 1000;
        }}

        .wiki-header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .wiki-logo {{
            font-size: 1.5em;
            font-weight: bold;
            color: var(--wiki-text);
            text-decoration: none;
        }}

        .wiki-logo span {{
            color: var(--wiki-blue);
        }}

        .wiki-search {{
            display: flex;
            gap: 10px;
        }}

        .wiki-search input {{
            padding: 6px 12px;
            border: 1px solid var(--wiki-border);
            border-radius: 2px;
            font-size: 14px;
            width: 300px;
        }}

        .wiki-search button {{
            padding: 6px 16px;
            background: var(--wiki-background);
            border: 1px solid var(--wiki-border);
            border-radius: 2px;
            cursor: pointer;
        }}

        /* Main layout */
        .wiki-main {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
            padding: 20px;
        }}

        /* Sidebar / TOC */
        .wiki-sidebar {{
            position: sticky;
            top: 70px;
            height: calc(100vh - 90px);
            overflow-y: auto;
            background: var(--wiki-content-bg);
            border: 1px solid var(--wiki-border);
            border-radius: 2px;
            padding: 15px;
        }}

        .toc-header {{
            font-size: 1.1em;
            font-weight: bold;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--wiki-border);
            margin-bottom: 15px;
        }}

        .toc-category {{
            margin-bottom: 20px;
        }}

        .toc-category-title {{
            font-size: 0.95em;
            font-weight: bold;
            color: var(--wiki-text);
            margin-bottom: 8px;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}

        .toc-list {{
            list-style: none;
            padding-left: 0;
        }}

        .toc-person {{
            margin-bottom: 8px;
        }}

        .toc-person-link {{
            color: var(--wiki-blue);
            text-decoration: none;
            font-weight: 500;
        }}

        .toc-person-link:hover {{
            text-decoration: underline;
        }}

        .toc-files {{
            list-style: none;
            padding-left: 15px;
            margin-top: 4px;
        }}

        .toc-files li {{
            font-size: 0.85em;
            margin-bottom: 2px;
        }}

        .toc-files a {{
            color: var(--wiki-text-light);
            text-decoration: none;
        }}

        .toc-files a:hover {{
            color: var(--wiki-blue);
            text-decoration: underline;
        }}

        /* Content area */
        .wiki-content {{
            background: var(--wiki-content-bg);
            border: 1px solid var(--wiki-border);
            border-radius: 2px;
            padding: 20px 30px;
        }}

        /* Page title */
        .page-title {{
            font-size: 1.8em;
            font-weight: normal;
            font-family: 'Linux Libertine', 'Georgia', 'Times', serif;
            border-bottom: 1px solid var(--wiki-header-border);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        /* Introduction box */
        .intro-box {{
            background: var(--wiki-infobox-bg);
            border: 1px solid var(--wiki-border);
            padding: 15px 20px;
            margin-bottom: 25px;
            border-radius: 2px;
        }}

        .intro-box h2 {{
            font-size: 1em;
            margin-bottom: 10px;
        }}

        .intro-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: var(--wiki-blue);
        }}

        .stat-label {{
            font-size: 0.85em;
            color: var(--wiki-text-light);
        }}

        /* Category sections */
        .category-section {{
            margin-bottom: 40px;
        }}

        .category-title {{
            font-size: 1.5em;
            font-weight: normal;
            font-family: 'Linux Libertine', 'Georgia', 'Times', serif;
            border-bottom: 1px solid var(--wiki-header-border);
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}

        /* Person articles */
        .person-article {{
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid var(--wiki-border);
        }}

        .person-header {{
            margin-bottom: 20px;
        }}

        .person-name {{
            font-size: 1.4em;
            font-weight: normal;
            font-family: 'Linux Libertine', 'Georgia', 'Times', serif;
            color: var(--wiki-text);
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }}

        .person-meta {{
            margin-top: 8px;
            font-size: 0.85em;
            color: var(--wiki-text-light);
        }}

        .doc-count {{
            background: var(--wiki-infobox-bg);
            padding: 2px 8px;
            border-radius: 3px;
            border: 1px solid var(--wiki-border);
        }}

        /* Document sections */
        .document-section {{
            margin-bottom: 25px;
            padding: 15px;
            background: var(--wiki-background);
            border: 1px solid var(--wiki-border);
            border-radius: 2px;
        }}

        .document-header {{
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--wiki-border);
        }}

        .document-type {{
            font-weight: bold;
            color: var(--wiki-text);
            font-size: 1.1em;
        }}

        .document-content {{
            font-size: 14px;
            line-height: 1.65;
        }}

        /* Wiki content styling */
        .wiki-h1 {{
            font-size: 1.3em;
            font-weight: bold;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid var(--wiki-border);
        }}

        .wiki-h2 {{
            font-size: 1.15em;
            font-weight: bold;
            margin: 18px 0 8px 0;
            padding-bottom: 3px;
            border-bottom: 1px solid #eee;
        }}

        .wiki-h3 {{
            font-size: 1.05em;
            font-weight: bold;
            margin: 15px 0 8px 0;
        }}

        .wiki-list {{
            margin: 10px 0;
            padding-left: 30px;
        }}

        .wiki-list li {{
            margin-bottom: 5px;
        }}

        .wiki-link {{
            color: var(--wiki-blue);
            text-decoration: none;
        }}

        .wiki-link:hover {{
            text-decoration: underline;
        }}

        .wiki-link:visited {{
            color: #795cb2;
        }}

        .wiki-quote {{
            margin: 15px 0;
            padding: 10px 20px;
            border-left: 4px solid var(--wiki-border);
            background: var(--wiki-infobox-bg);
            font-style: italic;
        }}

        .wiki-hr {{
            margin: 20px 0;
            border: none;
            border-top: 1px solid var(--wiki-border);
        }}

        .document-content p {{
            margin-bottom: 10px;
        }}

        .document-content strong {{
            font-weight: 600;
        }}

        /* Back to top link */
        .back-to-top {{
            margin-top: 15px;
            text-align: right;
        }}

        .back-to-top a {{
            color: var(--wiki-text-light);
            font-size: 0.85em;
            text-decoration: none;
        }}

        .back-to-top a:hover {{
            color: var(--wiki-blue);
        }}

        /* Footer */
        .wiki-footer {{
            background: var(--wiki-content-bg);
            border-top: 1px solid var(--wiki-border);
            padding: 20px;
            text-align: center;
            margin-top: 40px;
        }}

        .wiki-footer p {{
            color: var(--wiki-text-light);
            font-size: 0.85em;
        }}

        /* Responsive */
        @media (max-width: 900px) {{
            .wiki-main {{
                grid-template-columns: 1fr;
            }}

            .wiki-sidebar {{
                position: static;
                height: auto;
                max-height: 300px;
            }}
        }}

        /* Search highlighting */
        .highlight {{
            background-color: #fff3a8;
            padding: 1px 2px;
        }}

        /* Print styles */
        @media print {{
            .wiki-header, .wiki-sidebar, .back-to-top {{
                display: none;
            }}

            .wiki-main {{
                display: block;
            }}

            .wiki-content {{
                border: none;
            }}
        }}
    </style>
</head>
<body id="top">
    <header class="wiki-header">
        <div class="wiki-header-content">
            <a href="#top" class="wiki-logo">Brilliant<span>Minds</span></a>
            <div class="wiki-search">
                <input type="text" id="searchInput" placeholder="Search brilliant minds..." onkeyup="searchContent()">
                <button onclick="searchContent()">Search</button>
            </div>
        </div>
    </header>

    <main class="wiki-main">
        <aside class="wiki-sidebar">
            <div class="toc-header">Contents</div>
            {''.join(toc_sections)}
        </aside>

        <div class="wiki-content">
            <h1 class="page-title">Brilliant Minds Corpus</h1>

            <div class="intro-box">
                <h2>About this Collection</h2>
                <p>A comprehensive documentation corpus of 25 influential figures in computing, artificial intelligence,
                physics, and technology. Each entry includes biographical information, technical contributions,
                and a synthesized identity document designed for AI agent preloading.</p>

                <div class="intro-stats">
                    <div class="stat-item">
                        <div class="stat-number">{len(all_people)}</div>
                        <div class="stat-label">Brilliant Minds</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{sum(len(files) for files in all_people.values())}</div>
                        <div class="stat-label">Documents</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{len(CATEGORIES)}</div>
                        <div class="stat-label">Categories</div>
                    </div>
                </div>
            </div>

            {''.join(person_sections)}
        </div>
    </main>

    <footer class="wiki-footer">
        <p>Brilliant Minds Corpus - Generated for AI Agent Identity Preloading</p>
        <p>Inspired by Wikipedia's design. Content synthesized from multiple academic and professional sources.</p>
    </footer>

    <script>
        // Simple search functionality
        function searchContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const articles = document.querySelectorAll('.person-article');

            articles.forEach(article => {{
                const text = article.textContent.toLowerCase();
                const personName = article.querySelector('.person-name').textContent.toLowerCase();

                if (searchTerm === '' || text.includes(searchTerm) || personName.includes(searchTerm)) {{
                    article.style.display = 'block';
                }} else {{
                    article.style.display = 'none';
                }}
            }});

            // Also filter TOC
            const tocPersons = document.querySelectorAll('.toc-person');
            tocPersons.forEach(toc => {{
                const name = toc.querySelector('.toc-person-link').textContent.toLowerCase();
                if (searchTerm === '' || name.includes(searchTerm)) {{
                    toc.style.display = 'block';
                }} else {{
                    toc.style.display = 'none';
                }}
            }});
        }}

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>
'''

    return html

def main():
    html = generate_html()
    output_path = BASE_DIR / 'index.html'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    main()
