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

# 2. ਚੈਨਲ ਲਿਸਟ ਅਤੇ ਹਰ ਚੈਨਲ ਦੀ ਆਪਣੀ ਲਾਇਸੈਂਸ ਕੀ ਫੈਚ ਕਰਕੇ M3U ਬਣਾਉਣਾ
try:
    channels = requests.get("https://jtvxweb.pages.dev/jstr4web.json", timeout=10).json()
    
    m3u = '#EXTM3U\n'
    count = 0
    
    for ch in channels:
        name = ch.get('name', 'Unknown')
        url = ch.get('url', '')
        logo = ch.get('logo', '')
        category = ch.get('category', 'Unknown')
        group = f"JioTV+ ▶ | {category}"
        group_logo = "https://i.postimg.cc/52qG6sKt/STREAMXi.png"
        ch_id = ch.get('id', '')
        
        if not url:
            continue
            
        # ਜੇ JSON ਵਿੱਚ ਲਾਇਸੈਂਸ ਕੀ ਹੈ ਤਾਂ ਉਹ ਚੁੱਕ ਲਵੇਗਾ, ਨਹੀਂ ਤਾਂ 0000:0000 ਰੱਖ ਦੇਵੇਗਾ
        license_key = ch.get('key', '') or ch.get('license_key', '') or "0000:0000"
        
        final_url = f"{url}?{token}" if '?' not in url else f"{url}&{token}"
        
        # ਮੰਗਿਆ ਹੋਇਆ ਐਗਜ਼ੈਕਟ ਫਾਰਮੈਟ
        m3u += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{group}" group-logo="{group_logo}" tvg-logo="{logo}",{name}\n'
        m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
        m3u += f'#KODIPROP:inputstream.adaptive.license_key={license_key}\n'
        m3u += f'#EXTVLCOPT:http-user-agent=curl/8.20.0\n'
        m3u += f'#EXTHTTP:{{"cookie":"{token}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}\n'
        m3u += f'{final_url}\n'
        count += 1

    with open('myjiotv.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels in myjiotv.m3u.")
except Exception as e:
    print(f"Error: {e}")
