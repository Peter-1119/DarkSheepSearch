# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
tpl = open('site_template.html', encoding='utf-8').read()
_d = json.load(open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))

# 版本號在這裡再讀一次 version.json。
# 它本來是 build_site_data.py 寫進 site.json 的，但只改版本號、只重跑這支的話
# 就會拿到舊值 —— 版本號的用途正是「確認部署有沒有生效」，拿到舊值最要命。
# 讓最後一步以 version.json 為準，改完跑哪一支都對。
_v = json.load(open('version.json', encoding='utf-8'))
for _k, _f in (('siteVersion', 'site_version'), ('mapVersion', 'map_version'),
               ('author', 'author')):
    if _v.get(_f):
        if _d['meta'].get(_k) != _v[_f]:
            print('  %s: %s -> %s' % (_k, _d['meta'].get(_k), _v[_f]))
        _d['meta'][_k] = _v[_f]

data = json.dumps(_d, ensure_ascii=False, separators=(',', ':'))
# safe to embed inside <script type="application/json">
data = data.replace('</', '<\/').replace('\u2028', '\u2028').replace('\u2029', '\u2029')
out = tpl.replace('__DATA__', data)
p = os.path.join(ROOT, 'index.html')
open(p, 'w', encoding='utf-8').write(out)
print('wrote', p, '%.0f KB' % (len(out.encode('utf-8'))/1024))
