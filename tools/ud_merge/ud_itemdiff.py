import sys,re,difflib
sys.path.insert(0,r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/tools')
sys.stdout.reconfigure(encoding='utf-8')
import mpq,w3obj
from map_items import HOMO
D=r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/'
def load(f):
    return w3obj.parse(mpq.MPQ(D+f).read('war3map.w3t'),False)
O=load('UD_v3_82fix_opt.w3x'); N=load('UD_test_24_09_26_opt.w3x')
cl=lambda s: re.sub(r'\|c[0-9A-Fa-f]{8}|\|r','',(s or '')).translate(HOMO).replace('\r','')
for i in sys.argv[1:]:
    o=cl(O.get(i,{}).get('ubtn') and '' or O.get(i,{}).get('ides')); n=cl(N.get(i,{}).get('ides'))
    print('=====',i,N.get(i,{}).get('unam'), 'gold',O.get(i,{}).get('igol'),'->',N.get(i,{}).get('igol'),'abil',O.get(i,{}).get('iabi'),'->',N.get(i,{}).get('iabi'))
    for l in difflib.unified_diff(o.split('\n'),n.split('\n'),lineterm='',n=0):
        if not l.startswith(('---','+++','@@')): print(' ',l)
