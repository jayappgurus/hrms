import os
import django
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
django.setup()

def list_urls(lis, prefix=''):
    results = []
    for entry in lis:
        if hasattr(entry, 'url_patterns'):
            results.extend(list_urls(entry.url_patterns, prefix + (entry.namespace + ':' if entry.namespace else '')))
        else:
            results.append(f"{prefix}{entry.name}")
    return results

urls = list_urls(get_resolver().url_patterns)
with open('url_list_utf8.txt', 'w', encoding='utf-8') as f:
    for url in sorted(urls):
        f.write(f"{url}\n")
