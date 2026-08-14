import requests

# 1. Target M3U ਤੋਂ ਲਾਇਸੈਂਸ ਪ੍ਰੌਕਸੀ / ਕੀਅ ਫੈਚ ਕਰਨ ਦਾ ਫੰਕਸ਼ਨ
TARGET_M3U_URL = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"

proxy_map = {}
try:
    print(f"Fetching license proxy from target M3U: {TARGET_M3U_URL}")
    res = requests.get(TARGET_M3U_URL, timeout=10)
    if res.status_code == 200:
        lines = res.text.splitlines()
        current_id = ""
        for line in lines:
            line = line.strip()
            # tvg-id ਪੜ੍ਹਨਾ
            if 'tvg-id="' in line:
                try:
                    current_id = line.split('tvg-id="')[1].split('"')[0]
                except:
                    current_id = ""
            
            # ਲਾਇਸੈਂਸ ਪ੍ਰੌਕਸੀ / ਕੀਅ ਲਾਈਨ ਕੱਢਣਾ
            if ('license_key=' in line or 'KODIPROP:inputstream.adaptive.license_key' in line) and current_id:
                key_value = line.split('=')[-1].strip()
                proxy_map[current_id] = key_value
        print("Successfully mapped license proxies from target URL!")
    else:
        print("Warning: Could not fetch target M3U, using fallback license URLs.")
except Exception as e:
    print(f"Failed to fetch target proxy, error: {e}")

# 2. ਟੋਕਨ ਲੈਣ ਲਈ ਵੱਖ-ਵੱਖ ਲਿੰਕ
token_urls = [
    "https://allinonereborn2.online/jstrweb2/cookies.json",
    "https://allinonereborn2.online/jstrweb3/cookies.json",
    "https://allinonereborn2.online/jstrweb4/cookies.json"
]

token = ""
for url in token_urls:
    try:
        print(f"Trying to fetch token from: {url}")
        cookie_res = requests.get(url, timeout=10).json()
        
        for item in cookie_res:
            if "cookie" in item:
                token = item["cookie"]
                break
        if token:
            print("Token fetched successfully!")
            break
    except Exception as e:
        print(f"Failed with {url}, trying next...")

if not token:
    print("Error: Could not fetch token from any source!")
    exit()

# 3. ਚੈਨਲ ਲਿਸਟ ਫੈਚ ਕਰਨਾ ਅਤੇ ਨਵੀਂ M3U ਬਣਾਉਣਾ
try:
    print("Fetching channel list...")
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

        # Target M3U ਵਿੱਚੋਂ ਆਈ ਲਾਇਸੈਂਸ ਪ੍ਰੌਕਸੀ ਨੂੰ ਪਹਿਲ ਦੇਣੀ, ਜੇ ਨਾ ਮਿਲੇ ਤਾਂ ਆਪਣੀ ਡਿਫਾਲਟ ਵਰਤਣੀ
        license_key = proxy_map.get(ch_id) or ch.get('license_key') or ch.get('key') or f"https://ziotvplus.yowaimo.in/license/{ch_id}"
        
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
        
    print(f"Success! Generated {count} channels with updated license proxy.")
except Exception as e:
    print(f"Error: {e}")
