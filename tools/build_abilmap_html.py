# -*- coding: utf-8 -*-
"""把 data/abilmap.json 做成 abilmap.html：技能 × 機制的可篩選矩陣。

用法是反向查詢 —— 點一個標籤（例如「冰凍」「key 13 中繼」「FrostUnit」），
清單就只剩依賴它的技能，按英雄分組。改版時看 地圖版本差異.md 說哪支函式動了，
來這裡點那支函式，就知道要重驗哪些技能。
"""
import io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.stdout.reconfigure(encoding='utf-8')
D = json.load(io.open(os.path.join(ROOT, 'data', 'abilmap.json'), encoding='utf-8'))
H = {}
for a in D['abilities']:
    H.setdefault(a['hero'], {'n': a['hero_n'], 'ab': []})['ab'].append(a)

TPL = u'''<!doctype html>
<html lang="zh-Hant" data-theme="dark"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UD 圖鑑 · 技能機制矩陣</title>
<style>
:root{color-scheme:dark;--bg:#0a0c11;--bg-2:#0e1118;--surface:#141822;--surface-2:#1a1f2b;--line:#242a38;--line-2:#2f3646;
  --ink:#e8ebf2;--ink-2:#9aa3b8;--ink-3:#646d82;--accent:#ffb648;--str:#f2795b;--agi:#57d98a;--int:#54c6ec;--bar:#3987e5;
  font-family:system-ui,-apple-system,"Segoe UI","Noto Sans TC",sans-serif}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font-size:13px;line-height:1.5}
button,input{font:inherit;color:inherit}button{cursor:pointer}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.92em}
.wrap{max-width:1480px;margin:0 auto;padding:18px 22px 60px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--ink-2);margin-bottom:12px}
.ctrl{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin-bottom:12px}
.grp{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin:4px 0}
.grp .lab{font-size:11px;color:var(--ink-3);letter-spacing:.06em;text-transform:uppercase;width:92px;flex:none}
.chip{padding:3px 9px;border-radius:999px;border:1px solid var(--line-2);background:none;color:var(--ink-2);font-size:12px}
.chip:hover{color:var(--ink);border-color:var(--ink-3)}
.chip[aria-pressed="true"]{background:var(--surface-2);color:var(--ink);border-color:var(--accent)}
.chip .n{color:var(--ink-3);font-size:10.5px;margin-left:4px}
.chip[aria-pressed="true"] .n{color:var(--accent)}
input.q{background:var(--surface-2);border:1px solid var(--line-2);border-radius:8px;padding:5px 10px;width:220px}
.stat{color:var(--ink-2);margin:0 0 10px;font-size:12.5px}
.stat b{color:var(--ink)}
.hero{background:var(--surface);border:1px solid var(--line);border-radius:12px;margin-bottom:10px;overflow:hidden}
.hero>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:10px;padding:9px 14px}
.hero>summary::-webkit-details-marker{display:none}
.hero>summary b{font-size:14px}.hero>summary .c{color:var(--ink-3);font-size:12px;margin-left:auto}
.hero>summary i.a{width:10px;height:10px;border-radius:50%;border:2.5px solid var(--sc);display:inline-block;flex:none}
.hero .sc{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:860px;font-size:12px;table-layout:fixed}
th{text-align:left;color:var(--ink-3);font-weight:500;padding:4px 10px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:11px;letter-spacing:.04em}
td{padding:5px 10px;border-bottom:1px solid color-mix(in srgb,var(--line) 60%,transparent);vertical-align:top}
td.nm{white-space:normal}td.nm b{font-weight:600}td.nm code{color:var(--ink-3);margin-left:6px}
td.nm .k{font-size:10.5px;color:var(--ink-3);border:1px solid var(--line-2);border-radius:5px;padding:0 5px;margin-left:6px}
.tag{display:inline-block;padding:1px 7px;border-radius:6px;font-size:11px;margin:1px 3px 1px 0;border:1px solid var(--line-2);color:var(--ink-2)}
.tag.st{border-color:color-mix(in srgb,var(--accent) 40%,var(--line-2));color:var(--ink)}
.tag.fn{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:10.5px}
.tag.on{background:var(--surface-2);border-color:var(--accent);color:var(--ink)}
.tag.eng{border-style:dashed}
td.nat{color:var(--ink-3);font-style:italic}
.foot{margin-top:18px;color:var(--ink-3);font-size:12px;line-height:1.7}
</style></head><body><div class="wrap">
<h1>技能機制矩陣</h1>
<div class="sub">每個技能從程式碼抽出它依賴的共用函式、施加的狀態、hash key、傷害事件型態、縮放來源。點標籤反向查詢；改版時看 <code>地圖版本差異.md</code> 說哪支函式動了，來這裡點它。資料版本：<code>__MAP__</code></div>
<section class="ctrl">
  <div class="grp"><span class="lab">狀態</span><span id="f-status"></span></div>
  <div class="grp"><span class="lab">型態</span><span id="f-flag"></span></div>
  <div class="grp"><span class="lab">縮放</span><span id="f-scale"></span></div>
  <div class="grp"><span class="lab">引擎函式</span><span id="f-eng"></span></div>
  <div class="grp"><span class="lab">hash key</span><span id="f-key"></span></div>
  <div class="grp"><span class="lab">搜尋</span><input class="q" id="q" placeholder="技能名、英雄名、函式名、ID…"><button class="chip" id="clear">清除全部</button></div>
</section>
<p class="stat" id="stat"></p>
<div id="list"></div>
<footer class="foot">標籤的意思：<b>狀態</b>＝呼叫了對應的施加／結算函式；<b>key 13 中繼</b>＝傷害算英雄打的（吃 DefCof、帶穿透）；<b>純原生</b>＝JASS 裡沒有實作，效果全在物件欄位，改動只會出現在 w3a 的 diff；<b>吃裝備技能冷卻</b>＝內冷走 StartModCooldown。函式標籤有虛線框的是共用引擎函式。同一個技能可以同時有多個標籤；篩選是「全部都要符合」。</footer>
</div>
<script>
const D = __DATA__;
const $ = s => document.querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ATTR = {str:'var(--str)', agi:'var(--agi)', int:'var(--int)'};
const S = {status:new Set(), flag:new Set(), scale:new Set(), fn:new Set(), key:new Set(), q:''};
const ENG = new Set(D.engine_fns);
const KEYN = D.names.key;
function chips(box, kind, entries, label){
  box.innerHTML = entries.map(([k, n]) => `<button class="chip" data-k="${esc(kind)}" data-v="${esc(k)}" aria-pressed="${S[kind].has(k)}" title="${esc(kind==='key' ? (KEYN[k]||'') : '')}">${esc(label(k))}<span class="n">${n}</span></button>`).join('');
}
function renderCtrl(){
  const cnt = (m) => Object.entries(m).map(([k, v]) => [k, v.length]).sort((a, b) => b[1] - a[1]);
  chips($('#f-status'), 'status', cnt(D.by_status), k => (D.names.status[k]||[k])[0]);
  chips($('#f-flag'), 'flag', cnt(D.by_flag).concat([['native', D.abilities.filter(a=>a.native).length]]), k => (D.names.flag[k]||[k])[0]);
  chips($('#f-scale'), 'scale', cnt(D.by_scale), k => (D.names.scale[k]||[k])[0]);
  chips($('#f-eng'), 'fn', cnt(D.by_fn).filter(([k]) => ENG.has(k)), k => k);
  const keys = cnt(D.by_key).filter(([k]) => /^\\d+$/.test(k) && KEYN[k]);
  chips($('#f-key'), 'key', keys, k => 'key ' + k);
}
function match(a){
  for (const s of S.status) if (!a.status.includes(s)) return false;
  for (const f of S.flag) if (f === 'native' ? !a.native : !a.flags.includes(f)) return false;
  for (const s of S.scale) if (!a.scale.includes(s)) return false;
  for (const f of S.fn) if (!a.fns.includes(f) && !a.own_fns.includes(f)) return false;
  for (const k of S.key) if (!a.kr.includes(+k) && !a.kw.includes(+k)) return false;
  if (S.q){ const q = S.q.toLowerCase();
    const hay = [a.id, a.n.join(' '), a.hero_n.join(' '), a.fns.join(' '), a.own_fns.join(' ')].join(' ').toLowerCase();
    if (!hay.includes(q)) return false; }
  return true;
}
function tag(cls, txt, on){ return `<span class="tag ${cls}${on ? ' on' : ''}">${esc(txt)}</span>`; }
function renderList(){
  const heroes = Object.entries(__HEROES__);
  let total = 0, shown = 0, hn = 0, out = '';
  for (const [hid, h] of heroes){
    const abs = h.ab.filter(match); total += h.ab.length;
    if (!abs.length) continue;
    shown += abs.length; hn++;
    const attr = h.ab[0].attr || '';
    out += `<details class="hero" open><summary><i class="a" style="--sc:${ATTR[attr]||'var(--ink-3)'}"></i><b>${esc(h.n[0])}</b><span class="c">${abs.length} / ${h.ab.length}</span></summary>
      <div class="sc"><table><colgroup><col style="width:17%"><col style="width:9%"><col style="width:20%"><col style="width:14%"><col style="width:10%"><col style="width:20%"><col style="width:10%"></colgroup><thead><tr><th>技能</th><th>狀態</th><th>型態</th><th>縮放</th><th>hash key</th><th>共用函式</th><th>攻擊類型</th></tr></thead><tbody>${
      abs.map(a => `<tr>
        <td class="nm"><b>${esc(a.n[0])}</b><code>${a.id}</code>${a.kind !== 'hero' ? `<span class="k">${esc({innate:'固有',talent:'天賦',skin:'皮膚'}[a.kind]||a.kind)}</span>` : ''}${a.native ? '<span class="k">純原生</span>' : ''}</td>
        <td>${a.status.map(s => tag('st', (D.names.status[s]||[s])[0], S.status.has(s))).join('')}</td>
        <td>${a.flags.map(f => tag('', (D.names.flag[f]||[f])[0], S.flag.has(f))).join('')}${a.dmg_calls ? tag('', '傷害呼叫×' + a.dmg_calls) : ''}</td>
        <td>${a.scale.map(s => tag('', (D.names.scale[s]||[s])[0], S.scale.has(s))).join('')}</td>
        <td>${a.kr.concat(a.kw.filter(k => !a.kr.includes(k))).filter(k => KEYN[k]).map(k => `<span class="tag${S.key.has(String(k)) ? ' on' : ''}" title="${esc(KEYN[k])}">${a.kw.includes(k) && !a.kr.includes(k) ? '寫' : a.kw.includes(k) ? '讀寫' : ''} ${k}</span>`).join('')}</td>
        <td>${a.fns.filter(f => ENG.has(f)).map(f => tag('fn eng', f, S.fn.has(f))).join('')}${a.fns.filter(f => !ENG.has(f)).slice(0, 4).map(f => tag('fn', f, S.fn.has(f))).join('')}${a.fns.filter(f => !ENG.has(f)).length > 4 ? `<span class="tag">+${a.fns.filter(f => !ENG.has(f)).length - 4}</span>` : ''}</td>
        <td>${a.attack.map(x => tag('', x)).join('')}</td></tr>`).join('')}</tbody></table></div></details>`;
  }
  $('#list').innerHTML = out || '<p class="stat">沒有符合的技能</p>';
  const act = [...S.status, ...S.flag, ...S.scale, ...S.fn, ...S.key].length + (S.q ? 1 : 0);
  $('#stat').innerHTML = act ? `符合 <b>${shown}</b> 個技能，<b>${hn}</b> 隻英雄（共 ${total} 個）` : `共 <b>${total}</b> 個技能、${heroes.length} 隻英雄。點上面的標籤篩選。`;
}
function render(){ renderCtrl(); renderList(); }
document.querySelector('.ctrl').addEventListener('click', e => {
  const c = e.target.closest('.chip[data-k]'); if (!c) return;
  const set = S[c.dataset.k], v = c.dataset.v;
  set.has(v) ? set.delete(v) : set.add(v); render();
});
$('#list').addEventListener('click', e => {
  const t = e.target.closest('.tag.fn'); if (!t) return;
  const f = t.textContent.trim(); S.fn.has(f) ? S.fn.delete(f) : S.fn.add(f); render();
});
$('#q').addEventListener('input', e => { S.q = e.target.value.trim(); renderList(); });
$('#clear').addEventListener('click', () => { for (const k of ['status','flag','scale','fn','key']) S[k].clear(); S.q = ''; $('#q').value = ''; render(); });
const h = location.hash.slice(1);
if (h){ const [k, v] = h.split(':'); if (S[k]) S[k].add(decodeURIComponent(v)); }
render();
</script></body></html>
'''
# 給頁面用的精簡資料：每隻英雄的技能（帶 attr 給外環顏色）
heroes = json.load(io.open(os.path.join(ROOT, 'data', 'heroes.json'), encoding='utf-8'))['heroes']
attr = {h['id']: h['attr'] for h in heroes}
hero_js = {}
for hid, v in H.items():
    hero_js[hid] = {'n': v['n'], 'ab': [dict(a, attr=attr.get(hid, '')) for a in v['ab']]}
slim = {k: D[k] for k in ('by_status', 'by_flag', 'by_scale', 'by_fn', 'by_key', 'names', 'engine_fns')}
slim['abilities'] = [{'native': a['native']} for a in D['abilities']]
html = (TPL.replace('__DATA__', json.dumps(slim, ensure_ascii=False, separators=(',', ':')))
           .replace('__HEROES__', json.dumps(hero_js, ensure_ascii=False, separators=(',', ':')))
           .replace('__MAP__', D['map']))
dst = os.path.join(ROOT, 'abilmap.html')
io.open(dst, 'w', encoding='utf-8').write(html)
print('abilmap.html：%d 隻英雄、%d 個技能，%.0f KB' % (len(hero_js), len(D['abilities']), len(html.encode('utf-8')) / 1024))
