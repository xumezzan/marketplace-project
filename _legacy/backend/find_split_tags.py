import re

files = [
    '/Users/whomaun/Projects/services-marketplace/backend/marketplace/templates/marketplace/home.html',
    '/Users/whomaun/Projects/services-marketplace/backend/templates/base.html'
]

for filepath in files:
    print(f"Checking {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if '{% trans' in line and '%}' not in line:
            print(f"Split tag found at line {i+1}: {line.strip()}")
        elif '{% trans' in line:
            # Check if it's a multi-line string inside the tag (which is also invalid for trans)
            # But simple check: does it end with %}`?
            pass
