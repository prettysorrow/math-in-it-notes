#! /opt/homebrew/bin/python3
import os
import sys
import argparse
import re
from pathlib import Path

def natural_sort_key(entry):
    name = entry.name.removesuffix('.md')
    m = re.match(r'(\d+)\+?', name)
    if m:
        num = int(m.group(1))
        suffix = name[m.end():] if len(name) > m.end() else ''
        plus = 1 if '+' in name[:m.end()] else 0
        return (1, num, plus, suffix)
    return (0, '', name)

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
                f.write(src.read())
            f.write('\n---\n---\n---\n\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', required=True, help='output file path')
    args = parser.parse_args()
    root_dir = './notes/'
    write_md_files(root_dir, args.o)
