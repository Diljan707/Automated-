cat << 'EOF' > update_playlist.py
import requests

url_1173 = "https://raw.githubusercontent.com/Diljan707/Automated-/refs/heads/main/JioTV_Auto.m3u"
url_958 = "https://jhs-channels.rtxcric.workers.dev/playlist.m3u"
url_zee = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"
url_sony = "https://raw.githubusercontent.com/Diljan707/sony-hls/refs/heads/main/all_sony_live_tokens.m3u"

def fetch_playlist(url):
    try:
        r = requests.get(url, timeout=15)
        return r.text.splitlines() if r.status_code == 200 else []
    except: return []

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
            block = [lines[i]]
            i += 1
            while i < len(lines) and not lines[i].startswith("#EXTINF"):
                block.append(lines[i])
                i += 1
            name = extinf.split(",")[-1].strip().lower()
            channels[name] = block
        else: i += 1
    return channels

ch_1173 = parse_channels(lines_1173)
ch_958 = parse_channels(lines_958)
ch_zee = parse_channels(lines_zee)
ch_sony = parse_channels(lines_sony)

# 1. 1173 ਵਾਲੀ ਲਿਸਟ ਵਿੱਚੋਂ Star Sports, Zee ਅਤੇ Sony ਦੇ ਪੁਰਾਣੇ ਚੈਨਲ ਕੱਢਣੇ ਨੇ
final_list = {}
for n, b in ch_1173.items():
    if "star sports" in n or "zee" in n or "sony" in n:
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

# 4. Sony ਲਿੰਕ ਵਿੱਚੋਂ Sony Pal ਅਤੇ Sony Ten ਚੈਨਲ ਐਡ ਕਰਨੇ
target_sony_keywords = {
    "sony pal",
    "sony ten 1",
    "sony ten 2",
    "sony ten 3",
    "sony ten 4",
    "sony ten 5"
}
for n, b in ch_sony.items():
    if any(keyword in n for keyword in target_sony_keywords):
        final_list[n] = b

final_playlist = ["#EXTM3U"]
for b in final_list.values(): 
    final_playlist.extend(b)

with open("JioTV_Auto.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist) + "\n")

print("Success! Updated playlist generated.")
EOF

python3 update_playlist.py
