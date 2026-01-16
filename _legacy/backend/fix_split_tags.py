import re

filepath = '/Users/whomaun/Projects/services-marketplace/backend/marketplace/templates/marketplace/home.html'

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to match {% trans "..." %} where the string or the tag itself is split across lines
    # We look for {% trans followed by anything until %} but allowing newlines
    # And we replace the newlines and extra spaces with a single space
    
    def replacer(match):
        full_tag = match.group(0)
        # Replace newlines and multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', full_tag)
        # Ensure it looks like {% trans "..." %}
        return cleaned

    # This pattern matches {% trans "..." %} potentially spanning multiple lines
    # It assumes the string is quoted with double quotes
    pattern = r'\{%\s*trans\s+"[^"]*"\s*%\}' 
    # Wait, the previous regex failed because the string itself was split: "Start... \n ...end"
    # So the closing quote is on the next line.
    
    # Correct pattern: {% trans " ... " %}
    # We need to match {% trans " then content then " %}
    # Content can contain newlines.
    
    pattern = r'\{%\s*trans\s+"((?:[^"\\]|\\.)*)"\s*%\}'
    
    # However, re.sub with a function is better.
    # We need DOTALL to match across lines
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    if content != new_content:
        print(f"Fixing {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"No changes needed for {filepath}")

fix_file(filepath)
