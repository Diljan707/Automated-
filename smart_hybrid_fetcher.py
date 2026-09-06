import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

print("--- ਸਮਾਰਟ ਹਾਈਬ੍ਰਿਡ ਡਿਸ਼ ਟੀਵੀ ਫ਼ੈਚਰ (ਪ੍ਰਾਇਮਰੀ: ਬੋਟ API) ---")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Content-Type': 'application/json'
}

active_endpoint = None

# 1. ਸਭ ਤੋਂ ਪਹਿਲਾਂ ਸਭ ਤੋਂ ਪੱਕਾ ਅਤੇ ਪ੍ਰਾਇਮਰੀ ਬੋਟ ਲਿੰਕ ਚੈੱਕ ਕਰਨਾ
primary_bot_url = "https://chatbotapi.dishtv.in/API/Bot/GetChannels"

print("1. ਸਭ ਤੋਂ ਪਹਿਲਾਂ ਪ੍ਰਾਇਮਰੀ ਬੋਟ API ਦੀ ਜਾਂਚ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...")
try:
    r = requests.post(primary_bot_url, headers=headers, json={}, timeout=5)
    if r.status_code == 200 and ("Result" in r.text or "Channel" in r.text):
        active_endpoint = primary_bot_url
        print(f"ਸਫਲਤਾ! ਪ੍ਰਾਇਮਰੀ ਬੋਟ API ਕੰਮ ਕਰ ਰਹੀ ਹੈ: {active_endpoint}")
except:
    pass

# 2. ਜੇ ਕਿਸੇ ਵਜ੍ਹਾ ਕਰਕੇ ਬੋਟ ਲਿੰਕ ਕੰਮ ਨਾ ਕਰੇ, ਤਾਂ ਆਟੋ-ਡਿਸਕਵਰੀ ਸ਼ੁਰੂ ਕਰਨਾ
if not active_endpoint:
    print("ਪ੍ਰਾਇਮਰੀ ਬੋਟ ਰਿਸਪਾਂਸ ਨਹੀਂ ਦੇ ਰਿਹਾ, ਵੈੱਬਸਾਈਟ ਤੋਂ ਆਟੋ-ਸਕੈਨ ਸ਼ੁਰੂ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...")
    main_url = "https://www.dishtv.in/channel-guide.html"
    try:
        res = requests.get(main_url, headers=headers, timeout=10)
        if res.status_code == 200:
            text_content = res.text
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for script in soup.find_all('script', src=True):
                js_url = urljoin(main_url, script['src'])
                try:
                    js_res = requests.get(js_url, headers=headers, timeout=5)
                    if js_res.status_code == 200:
                        text_content += "\n" + js_res.text
                except:
                    pass

            # ਡੋਮੇਨ ਅਤੇ ਪਾਥ ਲੱਭ ਕੇ ਟੈਸਟ ਕਰਨਾ
            domains = re.findall(r'https?://([a-zA-Z0-9.-]*(?:api|bot|bizlogic)[a-zA-Z0-9.-]*\.dishtv\.in)', text_content, re.IGNORECASE)
            for d in set(domains):
                test_url = f"https://{d}/API/Bot/GetChannels"
                try:
                    tr = requests.post(test_url, headers=headers, json={}, timeout=3)
                    if tr.status_code == 200 and "Result" in tr.text:
                        active_endpoint = test_url
                        print(f"ਆਟੋ-ਡਿਸਕਵਰਡ API ਮిల్ ਗਈ: {active_endpoint}")
                        break
                except:
                    pass
                if active_endpoint:
                    break
    except Exception as e:
        print("ਸਕੈਨਿੰਗ ਐਰਰ:", e)

if not active_endpoint:
    print("\n[ਐਰਰ]: ਕੋਈ ਵੀ API ਕੰਮ ਨਹੀਂ ਕਰ ਸਕੀ!")
    exit()

# 3. ਚੈਨਲ ਅਤੇ LCN ਡਾਟਾ ਡਾਊਨਲੋਡ ਕਰਕੇ ਫ਼ਾਈਲ ਬਣਾਉਣਾ
try:
    print("3. ਚੈਨਲ ਅਤੇ LCN ਡਾਟਾ ਡਾਊਨਲੋਡ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...")
    response = requests.post(active_endpoint, headers=headers, json={}, timeout=15)
    data = response.json()
    
    packages = data.get("Result", [])
    channel_map = {}
    
    for pkg in packages:
        ch_list = pkg.get("Channells") or pkg.get("Channels")
        if ch_list and isinstance(ch_list, list):
            for ch in ch_list:
                name = ch.get("ChannelName")
                lcn = ch.get("LCN") or ch.get("ServiceID")
                if name and lcn:
                    try:
                        channel_map[int(lcn)] = name
                    except:
                        pass
                        
    sorted_channels = sorted(channel_map.items())
    
    if sorted_channels:
        filename = "dishtv_lcn_list.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for lcn, name in sorted_channels:
                f.write(f"{lcn}: {name}\n")
        print(f"\nਕੁੱਲ {len(sorted_channels)} ਚੈਨਲ ਸਫਲਤਾਪੂਰਵਕ '{filename}' ਵਿੱਚ ਸੇਵ ਹੋ ਗਏ ਹਨ!")
    else:
        print("ਡਾਟਾ ਮਿਲਿਆ ਪਰ ਚੈਨਲ ਮੈਪ ਨਹੀਂ ਹੋ ਸਕੇ।")

except Exception as e:
    print("ਪ੍ਰੋਸੈਸਿੰਗ ਐਰਰ:", e)
