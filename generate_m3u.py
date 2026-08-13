import requests

# ਟੋਕਨ ਲੈਣ ਲਈ ਵੱਖ-ਵੱਖ ਲਿੰਕ
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
        
        # JSON ਵਿੱਚੋਂ ਹਰ ਚੈਨਲ ਦੀ ਆਪਣੀ ਅਸਲ ਲਾਇਸੈਂਸ ਕੀਅ ਚੁੱਕਣਾ (ਕੁੰਜੀ ਦਾ ਨਾਂ ਕੀਅ-ਫਾਰਮੈਟ ਮੁਤਾਬਕ ਹੋਵੇਗਾ, ਜਿਵੇਂ license_key ਜਾਂ key)
        license_key = ch.get('license_key') or ch.get('key') or f"https://ziotvplus.yowaimo.in/license/{ch_id}"
        
        if not url:
            continue
            
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

