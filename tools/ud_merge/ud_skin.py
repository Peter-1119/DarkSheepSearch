# -*- coding: utf-8 -*-
"""版本字串與遊戲介面（war3mapSkin.txt）。
   UPKEEP_NONE 是資源列最右邊那格的文字；地圖名稱在 w3i、MPQ 檔頭、SetMapName 各有一份。"""

OLD_VER = '24.09.26'
VERSION = '24.09.27'

# war3mapSkin.txt 的俄文介面字串（鍵不變，只換值）
SKIN = {
    'TaurenClass': '殭屍',
    'ITEM_USE_TOOLTIP': '|CFFFED312可使用。|R|n',
    'ITEM_PAWN_TOOLTIP': '|cff808080可出售。|R',
    'UPKEEP_NONE': '|cFFA085EDUD test ' + VERSION,
    'DISCONNECT': '連線中斷',
    'COLON_GOLD_INCOME_RATE': '金幣收入：',
    'COLON_LUMBER': '積分：',
    'RESOURCE_UBERTIP_LUMBER': '用「-save」指令存檔你的積分。',
    'RESOURCE_UBERTIP_GOLD': '金幣來自收入。',
    'ARMOR_DIVINE': '類型：|Cffffcc00動能|R',
    'ARMORTIP_DIVINE_V0M': '動能護甲能減少多數物理攻擊的傷害，但會被攻城砲彈與魔法穿透。',
    'ARMORTIP_DIVINE': '動能護甲能減少多數物理攻擊的傷害，但會被攻城砲彈與魔法穿透。',
    'ARMORTIP_DIVINE_V0C': '動能護甲能減少多數物理攻擊的傷害，但會被攻城砲彈與魔法穿透。',
    'ARMORTIP_NONE_V0C': '再生肉身受到遠程投射物與砲擊的傷害很高。',
    'ARMORTIP_NONE': '再生肉身受到遠程投射物與砲擊的傷害很高。',
    'ARMORTIP_NONE_V0M': '再生肉身受到遠程投射物與砲擊的傷害很高。',
    'ARMOR_NONE': '類型：|Cffffcc00肉身|R',
}


def skin(data):
    lines, hit = data.decode('utf-8').split('\n'), set()
    for i, ln in enumerate(lines):
        k = ln.split('=', 1)[0].strip()
        if '=' in ln and k in SKIN:
            lines[i] = k + '=' + SKIN[k] + ('\r' if ln.endswith('\r') else '')
            hit.add(k)
    miss = set(SKIN) - hit
    assert not miss, 'war3mapSkin.txt 找不到：%r' % miss
    return '\n'.join(lines).encode('utf-8')


def ver(b):
    """bytes 裡的舊版本號換新（長度相同，檔頭可以直接覆寫）。"""
    return b.replace(OLD_VER.encode(), VERSION.encode())
