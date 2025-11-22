import re
import os

files_to_fix = [
    '/Users/whomaun/Projects/services-marketplace/backend/marketplace/templates/marketplace/home.html',
    '/Users/whomaun/Projects/services-marketplace/backend/templates/base.html'
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find {% trans "..." %} tags that might span multiple lines
    # We look for {% followed by optional whitespace, then trans, then the string, then %}
    # We use dotall to match across lines
    
    # Pattern 1: {% trans "string" %} where string might have newlines
    pattern1 = r'\{%\s*trans\s+"(.*?)"\s*%\}'
    
    def replace_func(match):
        inner_text = match.group(1)
        # Replace newlines and multiple spaces with a single space
        clean_text = ' '.join(inner_text.split())
        return f'{{% trans "{clean_text}" %}}'

    new_content = re.sub(pattern1, replace_func, content, flags=re.DOTALL)

    # Pattern 2: {% on one line, trans on next (split tag opening)
    # This is harder to catch with just one regex if they are very separated, but usually it's {% \n trans
    pattern2 = r'\{%\s*\n\s*trans\s+"(.*?)"\s*%\}'
    new_content = re.sub(pattern2, replace_func, new_content, flags=re.DOTALL)

    if content != new_content:
        print(f"Fixing {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"No changes needed for {filepath}")

for fp in files_to_fix:
    if os.path.exists(fp):
        fix_file(fp)
    else:
        print(f"File not found: {fp}")
