# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
tpl = open('site_template.html', encoding='utf-8').read()
data = open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8').read()
# safe to embed inside <script type="application/json">
data = data.replace('</', '<\/').replace('\u2028', '\u2028').replace('\u2029', '\u2029')
out = tpl.replace('__DATA__', data)
p = os.path.join(ROOT, 'index.html')
open(p, 'w', encoding='utf-8').write(out)
print('wrote', p, '%.0f KB' % (len(out.encode('utf-8'))/1024))
