#!/usr/bin/env python3
import json
import re
import sys


def heading_to_slug(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def extract_text(inlines):
    parts = []
    for item in inlines:
        t = item['t']
        if t == 'Str':
            parts.append(item['c'])
        elif t == 'Space' or t == 'SoftBreak':
            parts.append(' ')
        elif t == 'Math':
            parts.append(item['c'][1])
        elif t in ('Strong', 'Emph', 'Underline', 'Strikeout',
                   'Superscript', 'Subscript', 'SmallCaps'):
            parts.append(extract_text(item['c']))
    return ''.join(parts)


def walk_blocks(blocks):
    for block in blocks:
        if isinstance(block.get('c'), list):
            for child in block['c']:
                if isinstance(child, dict) and 'c' in child:
                    yield child
        if isinstance(block.get('c'), list):
            for sub in walk_blocks(block['c']):
                yield sub


def process(ast):
    for block in ast['blocks']:
        if block['t'] == 'Header':
            text = extract_text(block['c'][2])
            slug = heading_to_slug(text)
            if slug:
                block['c'][1][0] = slug
    return ast


if __name__ == '__main__':
    ast = json.load(sys.stdin)
    ast = process(ast)
    json.dump(ast, sys.stdout)
