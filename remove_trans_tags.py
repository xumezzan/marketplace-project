#!/usr/bin/env python3
"""
Script to remove Django i18n translation tags from templates.
Replaces {% trans "text" %} with just text
"""

import re
import os
from pathlib import Path

def remove_trans_tags(content):
    """Remove {% trans %} tags from template content"""
    
    # Remove {% load i18n %}
    content = re.sub(r'{%\s*load\s+i18n\s*%}\n?', '', content)
    
    # Replace {% trans "text" %} with text
    # Handle both single and double quotes
    content = re.sub(r'{%\s*trans\s+"([^"]+)"\s*%}', r'\1', content)
    content = re.sub(r"{%\s*trans\s+'([^']+)'\s*%}", r'\1', content)
    
    # Replace {% blocktrans %} ... {% endblocktrans %} with content inside
    content = re.sub(r'{%\s*blocktrans\s*%}(.*?){%\s*endblocktrans\s*%}', r'\1', content, flags=re.DOTALL)
    
    # Remove {% blocktranslate %} ... {% endblocktranslate %}
    content = re.sub(r'{%\s*blocktranslate\s*%}(.*?){%\s*endblocktranslate\s*%}', r'\1', content, flags=re.DOTALL)
    
    return content

def process_file(filepath):
    """Process a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has trans tags
        if '{% trans' not in content and '{% load i18n %}' not in content and '{% blocktrans' not in content:
            return False
        
        # Remove trans tags
        new_content = remove_trans_tags(content)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Processed: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    # Find all HTML templates
    backend_dir = Path(__file__).parent / 'backend'
    html_files = list(backend_dir.rglob('*.html'))
    
    print(f"Found {len(html_files)} HTML files")
    print("=" * 60)
    
    processed = 0
    for html_file in html_files:
        if process_file(html_file):
            processed += 1
    
    print("=" * 60)
    print(f"✓ Processed {processed} files with translation tags")
    print(f"✓ {len(html_files) - processed} files had no translation tags")
    print("\n✓ All translation tags removed!")

if __name__ == '__main__':
    main()
