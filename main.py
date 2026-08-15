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
    token = ""

# 2. ਚੈਨਲ ਲਿਸਟ ਫੈਚ ਕਰਕੇ M3U ਬਣਾਉਣਾ
try:
    channels = requests.get("https://jtvxweb.pages.dev/jstr4web.json", timeout=10).json()
    
    m3u = '#EXTM3U\n'
    count = 0
    
    for ch in channels:
        name = ch.get('name', 'Unknown')
        url = ch.get('url', '')
        logo = ch.get('logo', '')
        group = "JioTV+ ▶ | Unknown"
        group_logo = "https://i.postimg.cc/52qG6sKt/STREAMXi.png"
        ch_id = ch.get('id', '')
        
        if not url:
            continue
            
        # ਜੇ ਚੈਨਲ .mpd ਵਾਲਾ ਹੈ ਤਾਂ ਉਸਦੀ ਅਸਲੀ ਲਾਇਸੈਂਸ ਕੀ ਲੱਗ ਸਕਦੀ ਹੈ, ਨਹੀਂ ਤਾਂ 0000:0000
        license_key = "0000:0000"
        
        final_url = f"{url}?{token}" if token and '?' not in url else f"{url}&{token}" if token else url
        
        m3u += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{group}" group-logo="{group_logo}" tvg-logo="{logo}",{name}\n'
        m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
        m3u += f'#KODIPROP:inputstream.adaptive.license_key={license_key}\n'
        m3u += f'#EXTVLCOPT:http-user-agent=curl/8.20.0\n'
        m3u += f'#EXTHTTP:{{"cookie":"{token}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}\n'
        m3u += f'{final_url}\n\n'
        count += 1

    # ਫ਼ਾਈਲ ਨੂੰ JioTV_Auto.m3u ਨਾਂ ਨਾਲ ਸੇਵ ਕਰਨਾ
    with open('myjio.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels in JioTV_Auto.m3u.")
except Exception as e:
    print(f"Error: {e}")
