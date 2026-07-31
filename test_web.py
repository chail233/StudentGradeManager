from urllib.request import urlopen

pages = {
    '/': 'Dashboard',
    '/grades': 'Grades',
    '/analysis': 'Analysis',
    '/charts': 'Charts',
    '/clean': 'Clean'
}

for path, name in pages.items():
    try:
        resp = urlopen(f'http://127.0.0.1:5000{path}')
        print(f'{name}: {resp.getcode()} OK')
        content = resp.read().decode('utf-8')
        print(f'  Content length: {len(content)} bytes')
    except Exception as e:
        print(f'{name}: ERROR - {e}')