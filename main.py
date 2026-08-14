import requests

# 1. ਟੋਕਨ ਫੈਚ ਕਰਨਾ
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

# 2. ਚੈਨਲ ਲਿਸਟ ਬਣਾਉਣਾ (ਜියੋਟੀਵੀ ਲਾਇਸੈਂਸ ਯੂਆਰਐੱਲ ਨਾਲ)
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
            
        # ਇੱਥੇ ਹਰ ਚੈਨਲ ਦੀ ਆਈਡੀ ਨਾਲ ਅਸਲੀ ਲਾਇਸੈਂਸ URL ਬਣ ਜਾਵੇਗਾ
        license_key = f"https://jiotv.jio.com/license/{ch_id}"
        
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

    # ਫ਼ਾਈਲ ਦਾ ਨਾਂ myjio.m3u ਸੇਵ ਹੋਵੇਗਾ
    with open('myjio.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels in myjio.m3u.")
except Exception as e:
    print(f"Error: {e}")
