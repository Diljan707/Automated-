import requests

TARGET_M3U_URL = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"

# 1. ਟਰੈਕਟ M3U ਵਿੱਚੋਂ ਕੋਈ ਵੀ ਇੱਕ ਕਾਮਨ ਲਾਇਸੈਂਸ ਪ੍ਰੌਕਸੀ ਲੱਭਣਾ
common_proxy = ""
try:
    res = requests.get(TARGET_M3U_URL, timeout=10)
    if res.status_code == 200:
        for line in res.text.splitlines():
            line = line.strip()
            if ('license_key=' in line or 'KODIPROP:inputstream.adaptive.license_key' in line):
                key_value = line.split('=')[-1].strip()
                if key_value.startswith("http"):
                    common_proxy = key_value
                    break # ਪਹਿਲੀ ਮਿਲਣ ਵਾਲੀ ਕਾਮਨ ਪ੍ਰੌਕਸੀ ਚੁੱਕ ਲਵੋ
except Exception as e:
    print(f"Error fetching target proxy: {e}")

# ਜੇ ਓਥੋਂ ਨਾ ਮਿਲੇ ਤਾਂ ਆਪਣੀ ਡਿਫਾਲਟ ਲਾ ਦੇਣੀ
if not common_proxy:
    common_proxy = "https://ziotvplus.yowaimo.in/license/"

# 2. ਟੋਕਨ ਫੈਚ ਕਰਨਾ (ਆਲ-ਇਨ-ਵਨ ਵਾਲਾ ਤਰੀਕਾ)
token_urls = [
    "https://allinonereborn2.online/jstrweb2/cookies.json",
    "https://allinonereborn2.online/jstrweb3/cookies.json",
    "https://allinonereborn2.online/jstrweb4/cookies.json"
]

token = ""
for url in token_urls:
    try:
        cookie_res = requests.get(url, timeout=10).json()
        for item in cookie_res:
            if "cookie" in item:
                token = item["cookie"]
                break
        if token:
            break
    except:
        continue

if not token:
    print("Error: Could not fetch token!")
    exit()

# 3. ਚੈਨਲ ਲਿਸਟ ਬਣਾਉਣਾ
try:
    channels = requests.get("https://jtvxweb.pages.dev/jstr4web.json", timeout=10).json()
    
    m3u = '#EXTM3U\n'
    count = 0
    
    for ch in channels:
        name = ch.get('name', 'Unknown')
        url = ch.get('url', '')
        logo = ch.get('logo', '')
        group = ch.get('category', 'Entertainment')
        ch_id = ch.get('id', '')
        
        if not url:
            continue
            
        # ਜੇ ਚੈਨਲ ਦੀ ਆਪ ਦੀ ਪ੍ਰੌਕਸੀ ਬਣਦੀ ਹੈ ਜਾਂ ਕਾਮਨ ਵਰਤਣੀ ਹੈ
        license_key = f"{common_proxy}{ch_id}" if "ziotvplus" in common_proxy else common_proxy
        
        final_url = f"{url}?{token}" if '?' not in url else f"{url}&{token}"
        
        m3u += f'\n#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}", {name}\n'
        
        if '.mpd' in url:
            m3u += '#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
            m3u += '#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
            m3u += f'#KODIPROP:inputstream.adaptive.license_key={license_key}\n'
            
        m3u += '#EXTVLCOPT:http-user-agent=StreamFlex(StreamFlex; JioSTB) JioTVPlus-AndroidTv\n'
        m3u += f'#EXTVLCOPT:cookie="{token}"\n'
        m3u += f'{final_url}\n'
        count += 1

    with open('JioTV_Auto.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels.")
except Exception as e:
    print(f"Error: {e}")
