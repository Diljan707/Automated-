import re
import requests

url_1173 = "https://raw.githubusercontent.com/Diljan707/Automated-/refs/heads/main/JioTV_Auto.m3u"
url_958 = "https://jhs-channels.rtxcric.workers.dev/playlist.m3u"
url_zee = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"
url_sony = "https://raw.githubusercontent.com/Diljan707/sony-hls/refs/heads/main/all_sony_live_tokens.m3u"

def fetch_playlist(url):
    try:
        r = requests.get(url, timeout=15)
        return r.text.splitlines() if r.status_code == 200 else []
    except: 
        return []

lines_1173 = fetch_playlist(url_1173)
lines_958 = fetch_playlist(url_958)
lines_zee = fetch_playlist(url_zee)
lines_sony = fetch_playlist(url_sony)

def parse_channels(lines):
    channels = {}
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i]
            extinf = re.sub(r'group-title="[^"]*"\s*', '', extinf)
            block = [extinf]
            i += 1
            while i < len(lines) and not lines[i].startswith("#EXTINF"):
                block.append(lines[i])
                i += 1
            name = extinf.split(",")[-1].strip().lower()
            channels[name] = block
        else: 
            i += 1
    return channels

ch_1173 = parse_channels(lines_1173)
ch_958 = parse_channels(lines_958)
ch_zee = parse_channels(lines_zee)
ch_sony = parse_channels(lines_sony)

# 1. 1173 ਵਾਲੀ ਲਿਸਟ ਵਿੱਚੋਂ ਸਿਰਫ਼ Star Sports ਅਤੇ Zee ਕੱਢਣੇ ਨੇ (Sony Pal ਹੁਣ ਨਹੀਂ ਕੱਢਣਾ)
final_list = {}
for n, b in ch_1173.items():
    if "star sports" in n or "zee" in n:
        continue
    final_list[n] = b

# 2. ਖ਼ਾਸ ਡਿਜੀਟਲ ਸਟਾਰ ਸਪੋਰਟਸ ਚੈਨਲ ਐਡ ਕਰਨੇ
target_star_channels = {
    "star sports 1 digital",
    "star sports 1 hindi digital",
    "star sports 2 digital",
    "star sports 2 hindi digital",
    "star sports 3 digital",
    "star sports khel digital"
}
for n, b in ch_958.items():
    if any(target in n for target in target_star_channels):
        final_list[n] = b

# 3. Zio.m3u ਵਿੱਚੋਂ Zee ਵਾਲੇ ਚੈਨਲ ਐਡ ਕਰਨੇ
for n, b in ch_zee.items():
    if "zee" in n:
        final_list[n] = b

# 4. Sony ਲਿੰਕ ਵਿੱਚੋਂ ਸਿਰਫ਼ Sony Ten ਚੈਨਲ ਐਡ ਕਰਨੇ (Sony Pal 1173 ਵਾਲਾ ਪਹਿਲਾਂ ਹੀ ਆ ਚੁੱਕਾ ਹੈ)
target_sony_keywords = {
    "sony ten 1",
    "sony ten 2",
    "sony ten 3",
    "sony ten 4",
    "sony ten 5",
    "sony ten 6"
}
for n, b in ch_sony.items():
    if any(keyword in n for keyword in target_sony_keywords):
        final_list[n] = b

# Zee ਵਾਲੀ ਲਿਸਟ ਵਿੱਚੋਂ ਲਾਇਸੈਂਸ ਡੋਮੇਨ ਲੱਭਣਾ
def get_zee_license_domain():
    for z_name, z_block in ch_zee.items():
        for line in z_block:
            if "inputstream.adaptive.license_key" in line:
                parts = line.split("=", 1)
                if len(parts) == 2 and parts[1].strip() and "null" not in parts[1]:
                    return parts[1].strip()
    return ""

zee_domain_template = get_zee_license_domain()

# 5. ਸਿਰਫ਼ ਲਾਇਸੈਂਸ ਕੀਅ ਚੈੱਕ ਕਰਨਾ
verified_list = {}
for n, b in final_list.items():
    new_block = []
    has_null_key = False
    channel_id = ""
    
    for line in b:
        if "inputstream.adaptive.license_key" in line:
            val = line.split("=", 1)[-1].strip()
            if not val or val == "null" or "null" in val:
                has_null_key = True
                if "/" in val:
                    channel_id = val.split('/')[-1]

    if not channel_id:
        channel_id = n.replace(" ", "")

    for line in b:
        if "inputstream.adaptive.license_key" in line:
            val = line.split("=", 1)[-1].strip()
            if not val or val == "null" or "null" in val:
                if zee_domain_template:
                    base_domain = zee_domain_template.rsplit('/', 1)[0]
                    new_line = f"#KODIPROP:inputstream.adaptive.license_key={base_domain}/{channel_id}"
                    new_block.append(new_line)
                    continue
        new_block.append(line)

    verified_list[n] = new_block

final_playlist = ["#EXTM3U"]
for b in verified_list.values(): 
    final_playlist.extend(b)

with open("JioTV_Auto.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist) + "\n")

print("Success! Sony Pal kept from 1173 playlist.")
