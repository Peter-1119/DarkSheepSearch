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

# 只在本機看的頁面：資料另外放，不進 site.json，也不進公開的 index.html。
# 兩個檔一起產生 —— index.html 是要推上去的那份（沒有這些頁），
# index.local.html 是自己看的那份（有），已列入 .gitignore。
LOCAL_ONLY = {'gacha': os.path.join(ROOT, 'data', 'gacha.json')}


def strip_local(text):
    """把 @local:gacha .. @/local 之間的行整段拿掉（含標記那兩行）。
    標記都是各自語境的整行註解，所以整行刪掉之後剩下的檔案仍然合法。"""
    out, skip = [], False
    for line in text.splitlines(True):
        if '@local:' in line:
            skip = True
            continue
        if '@/local' in line:
            skip = False
            continue
        if not skip:
            out.append(line)
    return ''.join(out)


def emit(rec, name):
    body = json.dumps(rec, ensure_ascii=False, separators=(',', ':'))
    # safe to embed inside <script type="application/json">
    body = body.replace('</', '<' + chr(92) + '/')
    out = (tpl if 'local' in name else strip_local(tpl)).replace('__DATA__', body)
    p = os.path.join(ROOT, name)
    open(p, 'w', encoding='utf-8').write(out)
    print('wrote', p, '%.0f KB' % (len(out.encode('utf-8')) / 1024))


emit(_d, 'index.html')                       # 公開版：不含只在本機看的頁
extra = {k: json.load(open(v, encoding='utf-8'))
         for k, v in LOCAL_ONLY.items() if os.path.isfile(v)}
if extra:
    emit(dict(_d, **extra), 'index.local.html')
    print('  本機版多了：%s（index.local.html 不進版控）' % '、'.join(extra))
