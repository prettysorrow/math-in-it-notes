#! /opt/homebrew/bin/python3
import os
import sys
import argparse
import re
from pathlib import Path
import html as html_mod

CALLOUT_ICONS = {
    'note': '💬', 'tip': '💡', 'hint': '💡', 'important': '💡',
    'warning': '⚠️', 'caution': '⚠️', 'attention': '⚠️',
    'info': 'ℹ️', 'todo': 'ℹ️',
    'abstract': '📋', 'summary': '📋', 'tldr': '📋',
    'success': '✅', 'check': '✅', 'done': '✅',
    'question': '❓', 'help': '❓', 'faq': '❓',
    'failure': '❌', 'fail': '❌', 'danger': '❌',
    'bug': '🐛', 'example': '📝',
    'quote': '💭', 'cite': '💭',
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,sans-serif;
    font-size:12pt;line-height:1.6;color:#1a1a1a;max-width:210mm;
    margin:0 auto;padding:20mm 25mm
  }}
  h1{{font-size:1.6em;margin:1.5em 0 0.5em;border-bottom:2px solid #e0e0e0;padding-bottom:0.3em}}
  h2{{font-size:1.3em;margin:1.2em 0 0.4em}}
  h3{{font-size:1.1em;margin:1em 0 0.3em}}
  p{{margin:0.5em 0}}
  ul,ol{{margin:0.5em 0;padding-left:2em}}
  li{{margin:0.2em 0}}
  code{{
    font-family:"SF Mono",Menlo,Monaco,Consolas,monospace;
    background:#f4f4f4;padding:0.15em 0.4em;border-radius:3px;font-size:0.9em
  }}
  pre code{{display:block;padding:1em;overflow-x:auto;background:#f8f8f8;border:1px solid #e0e0e0;border-radius:6px}}
  blockquote{{
    margin:0.5em 0;padding:0.5em 1em;border-left:4px solid #d0d0d0;
    background:#fafafa;color:#555
  }}
  a{{color:#0969da;text-decoration:none}}
  a:hover{{text-decoration:underline}}
  hr{{border:none;border-top:1px solid #e0e0e0;margin:1em 0}}
  img{{max-width:100%;height:auto;display:block;margin:0.5em 0}}
  .callout{{
    margin:0.8em 0;padding:0.8em 1em;border-radius:8px;border-left:4px solid #888
  }}
  .callout-note{{background:#f0f6ff;border-left-color:#0969da}}
  .callout-tip,.callout-hint,.callout-important{{background:#f0fff4;border-left-color:#2da44e}}
  .callout-warning,.callout-caution,.callout-attention{{background:#fff8e8;border-left-color:#d4920b}}
  .callout-info,.callout-todo{{background:#f0f6ff;border-left-color:#0969da}}
  .callout-abstract,.callout-summary,.callout-tldr{{background:#f0f6ff;border-left-color:#5b5bd6}}
  .callout-success,.callout-check,.callout-done{{background:#f0fff4;border-left-color:#2da44e}}
  .callout-question,.callout-help,.callout-faq{{background:#faf0ff;border-left-color:#a475d9}}
  .callout-failure,.callout-fail,.callout-danger{{background:#fff0f0;border-left-color:#cf222e}}
  .callout-bug{{background:#fff0f0;border-left-color:#cf222e}}
  .callout-example{{background:#f0f6ff;border-left-color:#8250df}}
  .callout-quote,.callout-cite{{background:#fafafa;border-left-color:#888}}
  .callout-title{{font-weight:600;margin-bottom:0.3em}}
  .katex-display{{margin:0.5em 0;overflow-x:auto;overflow-y:hidden}}
  @media print{{
    body{{max-width:none;padding:0}}
    a{{color:#1a1a1a}}
    pre code{{white-space:pre-wrap;word-break:break-all}}
  }}
</style>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{
    delimiters:[
      {{left:'$$',right:'$$',display:true}},
      {{left:'$',right:'$',display:false}},
      {{left:'\\\\[',right:'\\\\]',display:true}},
    ],
    macros:{{"\\\\set":"\\\\{{#1\\\\}}"}}
  }})">
</script>
<title>{title}</title>
</head>
<body>
{body}
</body>
</html>'''


def natural_sort_key(entry):
    name = entry.name.removesuffix('.md')
    m = re.match(r'(\d+)\+?', name)
    if m:
        num = int(m.group(1))
        suffix = name[m.end():] if len(name) > m.end() else ''
        plus = 1 if '+' in name[:m.end()] else 0
        return (1, num, plus, suffix)
    return (0, '', name)


def heading_to_slug(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def fix_wiki_images(content):
    content = re.sub(
        r'!\[\[([^\]]+?)(?:\|\s*(\d+)\s*)?\]\]',
        lambda m: f'![ ](images/{m.group(1).strip()})' + (f'{{width={m.group(2)}px}}' if m.group(2) else ''),
        content,
    )
    return content


def fix_wiki_links(content):
    content = re.sub(
        r'(?<!!)\[\[([^\]|]+)\|([^\]]+)\]\]',
        lambda m: f'[{m.group(2).strip()}](#{heading_to_slug(m.group(1).strip())})',
        content,
    )
    content = re.sub(
        r'(?<!!)\[\[([^\]]+)\]\]',
        lambda m: f'[{m.group(1).strip()}](#{heading_to_slug(m.group(1).strip())})',
        content,
    )
    return content


LIST_RE = re.compile(r'^(\s*)([-*]\s|\d+[.)]\s)')
BLOCKQUOTE_LIST_RE = re.compile(r'^>\s*[-*]\s|^>\s*\d+[.)]\s')


def normalize_lists(content):
    lines = content.split('\n')
    result = []
    in_code_block = False
    prev_blank = True
    prev_was_list = False
    for line in lines:
        if line.startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            prev_blank = False
            prev_was_list = False
            continue
        if in_code_block:
            result.append(line)
            continue
        stripped = line.strip()
        is_list = bool(LIST_RE.match(line)) if stripped else False
        is_bq_list = bool(BLOCKQUOTE_LIST_RE.match(line)) if stripped else False
        needs_sep = (
            (is_list or is_bq_list)
            and not prev_blank
            and not prev_was_list
        )
        if needs_sep:
            result.append('' if is_list else '>')
        result.append(line)
        prev_blank = (not stripped) or stripped == '>'
        prev_was_list = bool(is_list or is_bq_list)
    return '\n'.join(result)


def write_md_files(root_dir, out_file):
    out_path = Path(out_file).resolve()
    with open(out_file, 'w', encoding='utf-8') as f:
        for entry in sorted(os.scandir(root_dir), key=natural_sort_key):
            if not entry.name.endswith('.md'):
                continue
            if Path(entry.path).resolve() == out_path:
                continue
            name = entry.name.removesuffix('.md')
            f.write(f'# {name}\n\n')
            with open(entry.path, encoding='utf-8') as src:
                content = src.read()
                content = fix_wiki_images(content)
                content = fix_wiki_links(content)
                content = normalize_lists(content)
            f.write(content)
            f.write('\n\n')


def escape_html(text):
    return html_mod.escape(text, quote=False)


# --- HTML generator ---

def extract_math(text):
    replacements = {}
    def save_math(m):
        key = f'\x00M{len(replacements)}\x00'
        replacements[key] = m.group(0)
        return key
    text = re.sub(r'\$\$(.+?)\$\$', save_math, text, flags=re.DOTALL)
    text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', save_math, text)
    return text, replacements


def extract_code_blocks(text):
    replacements = {}
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('```'):
            key = f'\x00C{len(replacements)}\x00'
            content = []
            lang = lines[i][3:].strip()
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                content.append(lines[i])
                i += 1
            i += 1
            inner = escape_html('\n'.join(content))
            if lang:
                replacements[key] = f'<pre><code class="language-{escape_html(lang)}">{inner}\n</code></pre>'
            else:
                replacements[key] = f'<pre><code>{inner}\n</code></pre>'
            result.append(key)
        else:
            result.append(lines[i])
            i += 1
    return '\n'.join(result), replacements


def inline_to_html(text):
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    text = re.sub(
        r'!\[\[([^\]]+?)(?:\|([^\]]*))?\]\]',
        lambda m: f'<img src="../images/{escape_html(m.group(1))}" alt="{escape_html(m.group(2) or "")}>',
        text,
    )
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', lambda m: f'<code>{escape_html(m.group(1))}</code>', text)
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
    return text


def blocks_to_html(md_text):
    lines = md_text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if line.startswith('\x00') and ('\x00C' in line or '\x00M' in line):
            result.append(line)
            i += 1
            continue

        if line.startswith('#'):
            level = len(line.split(' ')[0])
            h_text = line[level:].strip()
            result.append(f'<h{level}>{inline_to_html(h_text)}</h{level}>')
            i += 1
            continue

        if line.strip() == '---':
            result.append('<hr>')
            i += 1
            continue

        if line.startswith('> '):
            callout_lines = []
            while i < len(lines) and (lines[i].startswith('> ') or lines[i].startswith('>')):
                callout_lines.append(lines[i][2:] if lines[i].startswith('> ') else lines[i][1:])
                i += 1
            text = '\n'.join(callout_lines).strip()
            m = re.match(r'\[!(\w+)\]\s*(.*)', text, re.IGNORECASE)
            if m:
                ctype = m.group(1).lower()
                ctitle = m.group(2).strip()
                rest_text = text[m.end():].strip()
                icon = CALLOUT_ICONS.get(ctype, '💬')
                title_html = f'<div class="callout-title">{icon} {escape_html(ctitle) if ctitle else ctype.capitalize()}</div>' if True else ''
                content_html = inline_to_html(rest_text.replace('\n', '<br>\n'))
                result.append(f'<div class="callout callout-{ctype}">{title_html}<div class="callout-content">{content_html}</div></div>')
            else:
                result.append(f'<blockquote>{inline_to_html(text.replace("\n", "<br>"))}</blockquote>')
            continue

        if line.startswith('- ') or line.startswith('* '):
            items = []
            while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                items.append(lines[i][2:])
                i += 1
            lis = ''.join(f'<li>{inline_to_html(item)}</li>' for item in items)
            result.append(f'<ul>{lis}</ul>')
            continue

        if re.match(r'^\d+[.)]\s', line):
            items = []
            while i < len(lines) and re.match(r'^\d+[.)]\s', lines[i]):
                items.append(re.sub(r'^\d+[.)]\s', '', lines[i]))
                i += 1
            lis = ''.join(f'<li>{inline_to_html(item)}</li>' for item in items)
            result.append(f'<ol>{lis}</ol>')
            continue

        if line.startswith('<a ') or line.startswith('<a id'):
            result.append(line)
            i += 1
            continue

        para_lines = []
        while i < len(lines) and lines[i].strip():
            if lines[i].startswith('#') or lines[i].strip() == '---':
                break
            if lines[i].startswith('> ') or lines[i].startswith('- ') or re.match(r'^\d+[.)]\s', lines[i]):
                break
            if lines[i].startswith('```'):
                break
            if lines[i].startswith('\x00'):
                para_lines.append(lines[i])
            elif lines[i].strip():
                para_lines.append(lines[i])
            else:
                break
            i += 1
        if para_lines:
            p_text = inline_to_html('\n'.join(para_lines).replace('\n', '<br>\n'))
            result.append(f'<p>{p_text}</p>')

    return '\n'.join(result)


def wrap_template(body, title='Math in IT'):
    return HTML_TEMPLATE.format(title=escape_html(title), body=body)


def generate_html(md_path, html_path):
    with open(md_path, encoding='utf-8') as f:
        md_text = f.read()

    md_text, math_map = extract_math(md_text)
    md_text, code_map = extract_code_blocks(md_text)
    html_body = blocks_to_html(md_text)

    for key, val in sorted(code_map.items(), reverse=True):
        html_body = html_body.replace(key, val, 1)
    for key, val in sorted(math_map.items(), reverse=True):
        html_body = html_body.replace(key, val, 1)

    full_html = wrap_template(html_body)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)


# --- main ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', required=True, help='output file path')
    parser.add_argument('--pdf', action='store_true', help='also generate .html with KaTeX for PDF export')
    args = parser.parse_args()
    root_dir = './notes/'
    write_md_files(root_dir, args.o)
    if args.pdf:
        out_path = Path(args.o).resolve()
        html_file = out_path.with_suffix('.html')
        print('Generating HTML...')
        generate_html(str(out_path), str(html_file))
        print(f'HTML: {html_file}')
        print('  Open in browser → Cmd+P → Save as PDF')
