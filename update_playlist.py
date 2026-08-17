import re
import requests

url_1173 = "https://raw.githubusercontent.com/Diljan707/Automated-/refs/heads/main/JioTV_Auto.m3u"
url_958 = "https://jhs-channels.rtxcric.workers.dev/playlist.m3u"
url_zee = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"
url_sony = "https://raw.githubusercontent.com/Diljan707/sony-hls/refs/heads/main/all_sony_live_tokens.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_playlist(url):
    try:
        r = requests.get(url, timeout=15, headers=HEADERS)
        return r.text.splitlines() if r.status_code == 200 else []
    except Exception as e:
        print(f"Playlist fetch error: {e}")
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

            # group-title remove
            extinf = re.sub(
                r'group-title="[^"]*"\s*',
                '',
                extinf
            )

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


# --------------------------------------------------
# 1. 1173 playlist vicho Star Sports, Zee, Sony Pal remove
# --------------------------------------------------

final_list = {}

for n, b in ch_1173.items():

    if (
        "star sports" in n
        or "zee" in n
        or "sony pal" in n
    ):
        continue

    final_list[n] = b


# --------------------------------------------------
# 2. 958 playlist vicho selected Star Sports Digital
# --------------------------------------------------

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


# --------------------------------------------------
# 3. Zio playlist vicho Zee channels
# --------------------------------------------------

for n, b in ch_zee.items():

    if "zee" in n:
        final_list[n] = b


# --------------------------------------------------
# 4. Sony Pal + Sony Ten 1-6
# --------------------------------------------------

target_sony_keywords = {
    "sony pal",
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


# --------------------------------------------------
# Get stream URL
# --------------------------------------------------

def get_stream_url(block):

    for line in block:

        line = line.strip()

        if line and not line.startswith("#"):
            return line

    return ""


# --------------------------------------------------
# Check URL
# 401 / 403 / 302 = BROKEN
# --------------------------------------------------

def check_stream(url):

    if not url:
        return False, None

    try:

        # HEAD request WITHOUT following redirects
        res = requests.head(
            url,
            timeout=5,
            headers=HEADERS,
            allow_redirects=False
        )

        status = res.status_code

        # These statuses should trigger fallback
        if status in (401, 403, 302):
            return False, status

        # 200 = working
        if status == 200:
            return True, status

        # Some servers don't support HEAD.
        # Try GET, again WITHOUT redirects.
        res.close()

        res = requests.get(
            url,
            timeout=5,
            stream=True,
            headers=HEADERS,
            allow_redirects=False
        )

        status = res.status_code

        if status in (401, 403, 302):
            res.close()
            return False, status

        if status == 200:
            res.close()
            return True, status

        res.close()

        return False, status

    except Exception as e:

        return False, None


# --------------------------------------------------
# Smart fallback
# --------------------------------------------------

verified_list = {}

for n, b in final_list.items():

    stream_url = get_stream_url(b)

    working, status = check_stream(stream_url)

    # 401 / 403 / 302 or other failed status
    if not working:

        # Same channel exists in Zee source
        if n in ch_zee:

            print(
                f"[FALLBACK] {n} | "
                f"Status: {status} | "
                f"Using Zee source"
            )

            verified_list[n] = ch_zee[n]

        else:

            print(
                f"[KEEP] {n} | "
                f"Status: {status} | "
                f"No Zee fallback available"
            )

            verified_list[n] = b

    else:

        print(
            f"[OK] {n} | Status: {status}"
        )

        verified_list[n] = b


# --------------------------------------------------
# Generate final playlist
# --------------------------------------------------

final_playlist = ["#EXTM3U"]

for b in verified_list.values():
    final_playlist.extend(b)


with open(
    "JioTV_Auto.m3u8",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(final_playlist) + "\n"
    )


print()
print("====================================")
print("Success! Smart Fallback playlist generated.")
print("File: JioTV_Auto.m3u8")
print("====================================")
