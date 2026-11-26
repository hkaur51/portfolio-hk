"""Builds the GitHub Pages copy of the portfolio from the artifact's source (index.src.html) and a data snapshot."""
import json, re, shutil, os
R = '/home/claude/portfolio-hk'; S = '/home/claude/site'
BASE = 'https://hkaur51.github.io/portfolio-hk/'
media = json.load(open('/tmp/media_map.json'))
data = json.load(open(f'{R}/_src/data.json'))
txt = json.dumps(data)
txt = re.sub(r'/_blob/([A-Za-z0-9]+)', lambda m: BASE + media[m.group(1)], txt)  # links to uploaded files
data = json.loads(txt)
s = open(f'{S}/index.src.html').read()
s = s.replace('__BOXES__', open('/home/claude/thread_boxes.json').read().strip()).replace('__WIDE__', open('/home/claude/img/wide_geo.json').read().strip())
old = "const blob = id => id ? '/_blob/' + encodeURIComponent(id) : '';"
assert old in s
s = s.replace(old, "const blob = id => id ? ((window.__MEDIA || {})[id] || '') : '';")
shim = '<script>\nwindow.__STATIC = true;\nwindow.__MEDIA = ' + json.dumps(media) + ';\nwindow.__DATA = ' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + ''';
(() => {
  const doc = p => ({
    onSnapshot(cb) { setTimeout(() => { const d = window.__DATA[p]; cb({ exists: !!d, data: () => JSON.parse(JSON.stringify(d || {})), metadata: { fromCache: false } }); }, 0); return () => {}; },
    async get() { const d = window.__DATA[p]; return { exists: !!d, data: () => d }; },
    async set() {}
  });
  window.claude = { use: async n => n === 'db' ? { doc } : null };
})();
</script>
'''
i = s.index('<script>\n{')
s = s[:i] + shim + s[i:]
s = s.replace('<head>', '<head>\n<meta name="description" content="Dr. Harsimrat Kaur, MSPH, BDS: dentist, public health researcher and health tech builder.">', 1)
open(f'{R}/index.html', 'w').write(s)
for f in ['sleeve.jpg', 'bg-tall-v3.jpg', 'bg-wide-v3.jpg', 'me-still-v1.webp', 'me-v1.webp', 'name-tall-v2.png', 'name-wide-v2.png']:
    shutil.copy(f'{S}/{f}', f'{R}/{f}')
for d in ['fonts', 'manifesto']:
    if os.path.exists(f'{R}/{d}'): shutil.rmtree(f'{R}/{d}')
    shutil.copytree(f'{S}/{d}', f'{R}/{d}')
open(f'{R}/.nojekyll', 'w').write('')
print('built', len(s))
