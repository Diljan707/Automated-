import requests
import re

print("Starting M3U Generation...")

# 1. Asli Star Sports cookie URL ton dynamic cookie fetch karna (Jaise web player karda hai)
COOKIE_STAR_SPORTS = "https://allinonereborn2.online/jtv-fetch/jstarcookie/cookie.json"
dynamic_cookie = ""

try:
    print("Fetching live dynamic cookie...")
    res = requests.get(COOKIE_STAR_SPORTS, timeout=8)
    if res.status_code == 200:
        data = res.json()
        if data and "failed_results" in data:
            for item in data["failed_results"]:
                err_details = item.get("error_details", {})
                final_url = err_details.get("final_url", "")
                if "__hdnea__=" in final_url:
                    match = re.search(r'__hdnea__=([^&]+)', final_url)
                    if match:
                        dynamic_cookie = f"__hdnea__={match.group(1)}"
                        break
except Exception as e:
    print(f"Notice: Dynamic cookie fetch failed: {e}")

# 2. Je dynamic cookie na mile, taan fallback cookies try karo
if not dynamic_cookie:
    token_urls = [
        "https://allinonereborn2.online/jstrweb2/cookies.json",
        "https://allinonereborn2.online/jstrweb3/cookies.json",
        "https://allinonereborn2.online/jstrweb4/cookies.json"
    ]
    for url in token_urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                cookie_res = res.json()
                for item in cookie_res:
                    if isinstance(item, dict) and "cookie" in item:
                        dynamic_cookie = item["cookie"]
                        break
                if dynamic_cookie:
                    break
        except Exception:
            continue

# 3. Base Proxy URL extraction
base_proxy_url = "https://streamflexsmm.in/license/"
try:
    target_m3u_url = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/main/ZioMobile.m3u"
    res = requests.get(target_m3u_url, timeout=5)
    if res.status_code == 200:
        for line in res.text.splitlines():
            if 'license_key=' in line:
                l_key = line.split('license_key=')[1].strip()
                if l_key and l_key != "null:null":
                    match = re.search(r'(https?://[^\s]+?/)(?:\d+/)?$', l_key)
                    if match:
                        base_proxy_url = match.group(1)
                    else:
                        base_proxy_url = re.sub(r'\d+/?$', '', l_key)
                    break
except Exception:
    pass

# 4. Main channels JSON fetch te M3U creation
try:
    print("Fetching channels JSON...")
    channels_res = requests.get("https://jjtvxweb.pages.dev/jstr4web.json", timeout=10)
    channels = channels_res.json()
    
    m3u = '#EXTM3U\n'
    count = 0
    
    for ch in channels:
        name = ch.get('name', 'Unknown')
        url = ch.get('url', '')
        logo = ch.get('logo', '')
        category = ch.get('category', 'Unknown')
        group = f"JioTV+ ▶ | {category}"
        group_logo = "https://i.postimg.cc/52qG6sKt/STREAMXi.png"
        
        ch_id = str(ch.get('id', ''))
        
        if not url:
            continue
            
        key_id = ch.get('keyId', '')
        key_val = ch.get('key', '')
        
        has_clearkey = key_id and key_val and key_id != "null" and key_val != "null"
        
        # Stream URL de nal dynamic cookie attach karna
        final_url = f"{url}?{dynamic_cookie}" if dynamic_cookie and '?' not in url else f"{url}&{dynamic_cookie}" if dynamic_cookie else url
        
        m3u += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{group}" group-logo="{group_logo}" tvg-logo="{logo}",{name}\n'
        
        if has_clearkey:
            license_key = f"{key_id}:{key_val}"
            m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
            m3u += f'#KODIPROP:inputstream.adaptive.license_key={license_key}\n'
        else:
            custom_license_proxy = f"{base_proxy_url}{ch_id}/"
            m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
            m3u += f'#KODIPROP:inputstream.adaptive.license_key={custom_license_proxy}\n'
            
        m3u += f'#EXTVLCOPT:http-user-agent=plaYtv/7.1.5\n'
        if dynamic_cookie:
            m3u += f'#EXTHTTP:{{"cookie":"{dynamic_cookie}","Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}\n'
        else:
            m3u += f'#EXTHTTP:{{"Origin":"https://www.jiotv.com/","Referer":"https://www.jiotv.com/"}}\n'
            
        m3u += f'{final_url}\n\n'
        count += 1

    filename = 'JioTV_Auto.m3u'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(m3u)
        
    print(f"Success! Generated {count} channels in {filename}.")

except Exception as e:
    print(f"Error occurred: {e}")
