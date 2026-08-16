import requests

url_1173 = "https://raw.githubusercontent.com/Diljan707/Automated-/refs/heads/main/JioTV_Auto.m3u"
url_958 = "https://jhs-channels.rtxcric.workers.dev/playlist.m3u"

def fetch_playlist(url):
    try:
        r = requests.get(url, timeout=15)
        return r.text.splitlines() if r.status_code == 200 else []
    except: return []

lines_1173 = fetch_playlist(url_1173)
lines_958 = fetch_playlist(url_958)

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

# 1. ਪਹਿਲੀ ਲਿਸਟ ਵਿੱਚੋਂ ਸਿਰਫ਼ Star Sports ਕੱਢਣੇ ਨੇ (Zee ਨੂੰ ਹੱਥ ਨਹੀਂ ਲਾਇਆ)
final_list = {
    n: b for n, b in ch_1173.items() 
    if "star sports" not in n
}

# 2. ਤੁਹਾਡੇ ਖ਼ਾਸ ਡਿਜੀਟਲ ਸਟਾਰ ਸਪੋਰਟਸ ਚੈਨਲਾਂ ਦੀ ਸੂਚੀ
target_star_channels = {
    "star sports 1 digital",
    "star sports 1 hindi digital",
    "star sports 2 digital",
    "star sports 2 hindi digital",
    "star sports 3 digital",
    "star sports khel digital"
}

for n, b in ch_958.items():
    # ਦੂਜੀ ਲਿਸਟ ਵਿੱਚੋਂ ਸਿਰਫ਼ ਤੁਹਾਡੇ ਦੱਸੇ ਹੋਏ ਖ਼ਾਸ ਡਿਜੀਟਲ Star Sports ਚੈਨਲ ਹੀ ਲੈਣੇ ਹਨ
    if any(target in n for target in target_star_channels):
        final_list[n] = b

final_playlist = ["#EXTM3U"]
for b in final_list.values(): final_playlist.extend(b)

with open("JioTV_Auto.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(final_playlist) + "\n")

print("Success! Playlist generated.")
