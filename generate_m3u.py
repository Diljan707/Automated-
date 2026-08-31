import requests
import re

COOKIE_STAR_SPORTS = "https://allinonereborn2.online/jtv-fetch/jstarcookie/cookie.json"
token_urls = [
    "https://allinonereborn2.online/jstrweb2/cookies.json",
    "https://allinonereborn2.online/jstrweb3/cookies.json",
    "https://allinonereborn2.online/jstrweb4/cookies.json"
]

def get_channel_token(ch_id):
    try:
        res = requests.get(COOKIE_STAR_SPORTS, timeout=8).json()
        if res and "failed_results" in res:
            for item in res["failed_results"]:
                if str(item.get("channel_id")) == str(ch_id):
                    err_details = item.get("error_details", {})
                    final_url = err_details.get("final_url", "")
                    if "__hdnea__=" in final_url:
                        match = re.search(r'__hdnea__=([^&]+)', final_url)
                        if match:
                            return f"__hdnea__={match.group(1)}"
    except:
        pass

    for url in token_urls:
        try:
            cookie_res = requests.get(url, timeout=8).json()
            if isinstance(cookie_res, list):
                for item in cookie_res:
                    if "cookie" in item:
                        return item["cookie"]
        except:
            continue
    return ""

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

# ਟਰਗਟ URL ਤੋਂ ਸਿਰਫ਼ ਲਾਇਸੈਂਸ ਪ੍ਰੌਕਸੀ ਦਾ ਮੁੱਢਲਾ ਹਿੱਸਾ (Base Proxy URL) ਕੱਢਣਾ
base_proxy_url = ""
try:
    target_m3u_url = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/main/ZioMobile.m3u"
    res = requests.get(target_m3u_url, timeout=10)
    if res.status_code == 200:
        lines = res.text.splitlines()
        for line in lines:
            if 'license_key=' in line:
                l_key = line.split('license_key=')[1].strip()
                if l_key and l_key != "null:null":
                    # ਜੇ ਲਿੰਕ ਵਿੱਚ ਅਖ਼ੀਰ ਵਿੱਚ ਕੋਈ ਨੰਬਰ/ID ਲੱਗੀ ਹੈ, ਉਸਨੂੰ ਹਟਾ ਕੇ ਬੇਸ URL ਬਣਾਉਣਾ
                    match = re.search(r'(https?://[^\s]+?/)(?:\d+/)?$', l_key)
                    if not match:
                        match_num = re.sub(r'\d+/?$', '', l_key)
                        base_proxy_url = match_num
                    else:
                        base_proxy_url = match.group(1)
                    break
except Exception as e:
    print(f"Warning: Could not fetch base proxy: {e}")

# ਜੇ ਬੇਸ ਪ੍ਰੌਕਸੀ ਨਾ ਮਿਲੇ ਤਾਂ ਡਿਫਾਲਟ
if not base_proxy_url:
    base_proxy_url = "https://streamflexsmm.in/license/"

try:
    channels = requests.get("https://jjtvxweb.pages.dev/jstr4web.json", timeout=10).json()
    
    m3u = '#EXTM3U\n'
    count = 0
    
    for ch in channels:
        name = ch.get('name', 'Unknown')
        url = ch.get('url', '')
        logo = ch.get('logo', '')
        category = ch.get('category', 'Unknown')
        group = f"JioTV+ ▶ | {category}"
        group_logo = "https://i.postimg.cc/52qG6sKt/STREAMXi.png"
        
        # ਤੁਹਾਡੀ ਆਪਣੀ ਪਲੇਲਿਸਟ ਵਾਲੀ ਚੈਨਲ ID
        ch_id = str(ch.get('id', ''))
        
        if not url:
            continue
            
        key_id = ch.get('keyId', '')
        key_val = ch.get('key', '')
        
        has_clearkey = key_id and key_val and key_id != "null" and key_val != "null"
        
        # Har channel da apna dynamic token ya fallback global token
        ch_token = get_channel_token(ch_id) or token
        
        final_url = f"{url}?{ch_token}" if ch_token and '?' not in url else f"{url}&{ch_token}" if ch_token else url
        
        m3u += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{group}" group-logo="{group_logo}" tvg-logo="{logo}",{name}\n'
        
        if has_clearkey:
            license_key = f"{key_id}:{key_val}"
            m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
            m3u += f'#KODIPROP:inputstream.adaptive.license_key={license_key}\n'
        else:
            # ਜਿੱਥੇ ਕਲੀਅਰ ਕੀ null ਹੈ, ਉੱਥੇ ਬੇਸ ਪ੍ਰੌਕਸੀ ਦੇ ਨਾਲ ਇਸ ਚੈਨਲ ਦੀ ਆਪਣੀ ID ਲੱਗ ਜਾਵੇਗੀ
            custom_license_proxy = f"{base_proxy_url}{ch_id}/"
            m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
            m3u += f'#KODIPROP:inputstream.adaptive.license_key={custom_license_proxy}\n'
            
        m3u += f'#EXTVLCOPT:http-user-agent=plaYtv/7.1.5\n'
        if ch_token:
            m3u += f'#EXTHTTP:{{"cookie":"{ch_token}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}\n'
        else:
            m3u += f'#EXTHTTP:{{"Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}\n'
            
        m3u += f'{final_url}\n\n'
        count += 1

    filename = 'JioTV_Auto.m3u'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels in {filename}.")
except Exception as e:
    print(f"Error: {e}")
                            
