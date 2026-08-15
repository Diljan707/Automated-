import requests

TARGET_M3U_URL = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"

# 1. ਟਰੈਕਟ M3U ਤੋਂ ਸਿਰਫ਼ ਪ੍ਰੌਕਸੀ ਕੱਢਣਾ (ਬਿਨਾਂ ਕਿਸੇ ਫਾਲਬੈਕ ਦੇ)
common_proxy = ""
try:
    print(f"Fetching target M3U from: {TARGET_M3U_URL}")
    res = requests.get(TARGET_M3U_URL, timeout=10)
    if res.status_code == 200:
        for line in res.text.splitlines():
            line = line.strip()
            if ('license_key=' in line or 'KODIPROP:inputstream.adaptive.license_key' in line):
                key_value = line.split('=')[-1].strip()
                if key_value.startswith("http"):
                    if "/license/" in key_value:
                        common_proxy = key_value.split("/license/")[0] + "/license/"
                    else:
                        common_proxy = key_value
                    break
        print(f"Extracted Proxy: {common_proxy}")
except Exception as e:
    print(f"Error fetching target proxy: {e}")

# 2. ਟੋਕਨ ਫੈਚ ਕਰਨਾ (Error: data.map ਤੋਂ ਬਚਣ ਲਈ ਸੇਫ਼ਟੀ ਚੈੱਕ ਨਾਲ)
token_urls = [
    "https://allinonereborn2.online/jstrweb2/cookies.json",
    "https://allinonereborn2.online/jstrweb3/cookies.json",
    "https://allinonereborn2.online/jstrweb4/cookies.json"
]

# ਸੇਫ਼ਟੀ ਲਈ ਡਿਫਾਲਟ ਵਰਕਿੰਗ ਟੋਕਨ
token = "__hdnea__=st=1786759237~exp=1786780837~acl=/*~hmac=8680f4ca0d237682af594af4311ea6165cc7176853d72ecea762b88f40c155a2"

for url in token_urls:
    try:
        cookie_res = requests.get(url, timeout=10).json()
        if isinstance(cookie_res, list):
            for item in cookie_res:
                if isinstance(item, dict) and "cookie" in item:
                    val = item["cookie"]
                    if val and "Error" not in val:
                        token = val
                        break
        break
    except:
        continue

# 3. ਚੈਨਲ ਲਿਸਟ ਬਣਾਉਣਾ (ਘੱਟ ਲੇਟੈਂਸੀ ਅਤੇ ਬਫਰਿੰਗ ਰੋਕਣ ਵਾਲੇ ਪੈਰਾਮੀਟਰਾਂ ਨਾਲ)
try:
    channels_res = requests.get("https://jtvxweb.pages.dev/jstr4web.json", timeout=10).json()
    
    if not isinstance(channels_res, list):
        channels = []
    else:
        channels = channels_res
        
    m3u = '#EXTM3U\n'
    count = 0
    
    for ch in channels:
        if not isinstance(ch, dict):
            continue
            
        name = ch.get('name', 'Unknown')
        url = ch.get('url', '')
        logo = ch.get('logo', '')
        group = ch.get('category', 'Entertainment')
        ch_id = ch.get('id', '')
        
        if not url:
            continue
            
        license_key = f"{common_proxy}{ch_id}" if not common_proxy.endswith(ch_id) else common_proxy
        
        final_url = f"{url}?{token}" if '?' not in url else f"{url}&{token}"
        
        # .mpd ਲਿੰਕਸ ਲਈ ਲਾਈਵ ਡਿਲੇਅ ਜ਼ੀਰੋ ਕਰਨਾ
        if '.mpd' in url and 'live_delay=0' not in final_url:
            final_url = f"{final_url}&live_delay=0" if '?' in final_url else f"{final_url}?live_delay=0"
        
        m3u += f'\n#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}", {name}\n'
        
        if '.mpd' in url:
            m3u += '#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
            m3u += '#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
            m3u += f'#KODIPROP:inputstream.adaptive.license_key={license_key}\n'
            
        # ਲੇਟੈਂਸੀ ਘਟਾਉਣ ਅਤੇ ਬਫਰਿੰਗ ਰੋਕਣ ਲਈ ਵਾਧੂ ਆਪਸ਼ਨਜ਼
        m3u += '#EXTVLCOPT:network-caching=300\n'
        m3u += '#EXTVLCOPT:file-caching=300\n'
        m3u += '#EXTVLCOPT:http-user-agent=StreamFlex(StreamFlex; JioSTB) JioTVPlus-AndroidTv\n'
        m3u += f'#EXTVLCOPT:cookie="{token}"\n'
        m3u += f'{final_url}\n'
        count += 1

    with open('JioTV_Auto.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels with low-latency settings.")
except Exception as e:
    print(f"Error: {e}")
