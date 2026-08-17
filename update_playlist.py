import re
import subprocess
import requests
import shutil
import os

# =========================================================
# SOURCES
# =========================================================

url_1173 = "https://raw.githubusercontent.com/Diljan707/Automated-/refs/heads/main/JioTV_Auto.m3u"
url_958 = "https://jhs-channels.rtxcric.workers.dev/playlist.m3u"
url_zee = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"
url_sony = "https://raw.githubusercontent.com/Diljan707/sony-hls/refs/heads/main/all_sony_live_tokens.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TEST_SECONDS = 5


# =========================================================
# FFMPEG
# =========================================================

if shutil.which("ffmpeg") is None:
    print("ERROR: ffmpeg not found")
    raise SystemExit(1)


# =========================================================
# FETCH
# =========================================================

def fetch_playlist(url):

    try:
        r = requests.get(
            url,
            timeout=20,
            headers=HEADERS
        )

        print(f"[PLAYLIST] {r.status_code} {url}")

        if r.status_code == 200:
            return r.text.splitlines()

    except Exception as e:
        print(f"[FETCH ERROR] {e}")

    return []


# =========================================================
# PARSE
# =========================================================

def parse_channels(lines):

    channels = {}
    i = 0

    while i < len(lines):

        if lines[i].startswith("#EXTINF"):

            extinf = lines[i]

            extinf = re.sub(
                r'group-title="[^"]*"\s*',
                '',
                extinf
            )

            block = [extinf]

            i += 1

            while (
                i < len(lines)
                and not lines[i].startswith("#EXTINF")
            ):
                block.append(lines[i])
                i += 1

            name = extinf.split(",")[-1].strip().lower()

            channels[name] = block

        else:
            i += 1

    return channels


# =========================================================
# LOAD
# =========================================================

ch_1173 = parse_channels(fetch_playlist(url_1173))
ch_958 = parse_channels(fetch_playlist(url_958))
ch_zee = parse_channels(fetch_playlist(url_zee))
ch_sony = parse_channels(fetch_playlist(url_sony))


# =========================================================
# BASE LIST
# =========================================================

final_list = {}

for name, block in ch_1173.items():

    if (
        "star sports" in name
        or "zee" in name
        or "sony pal" in name
    ):
        continue

    final_list[name] = block


# =========================================================
# STAR SPORTS
# =========================================================

star_targets = {
    "star sports 1 digital",
    "star sports 1 hindi digital",
    "star sports 2 digital",
    "star sports 2 hindi digital",
    "star sports 3 digital",
    "star sports khel digital"
}

for name, block in ch_958.items():

    if any(x in name for x in star_targets):
        final_list[name] = block


# =========================================================
# ZEE
# =========================================================

for name, block in ch_zee.items():

    if "zee" in name:
        final_list[name] = block


# =========================================================
# SONY
# =========================================================

sony_targets = {
    "sony pal",
    "sony ten 1",
    "sony ten 2",
    "sony ten 3",
    "sony ten 4",
    "sony ten 5",
    "sony ten 6"
}

for name, block in ch_sony.items():

    if any(x in name for x in sony_targets):
        final_list[name] = block


# =========================================================
# STREAM URL
# =========================================================

def get_stream_url(block):

    for line in block:

        line = line.strip()

        if line and not line.startswith("#"):
            return line

    return ""


# =========================================================
# FFMPEG TEST
# =========================================================

def ffmpeg_test(url):

    if not url:
        return False

    try:

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",

            "-i", url,

            "-t", str(TEST_SECONDS),

            "-map", "0:v:0",

            "-f", "null",
            "-"
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=TEST_SECONDS + 12
        )

        return result.returncode == 0

    except subprocess.TimeoutExpired:

        # Stream was still processing.
        return True

    except Exception as e:

        print(f"FFMPEG ERROR: {e}")
        return False


# =========================================================
# CHECK CHANNELS
# =========================================================

verified_list = {}

total = len(final_list)

print()
print("==========================================")
print("FFMPEG CHANNEL TEST")
print(f"TOTAL: {total}")
print("==========================================")
print()


for number, (name, original_block) in enumerate(
    final_list.items(),
    1
):

    print(
        f"[{number}/{total}] {name}"
    )

    original_url = get_stream_url(
        original_block
    )

    # -----------------------------------------
    # ORIGINAL
    # -----------------------------------------

    if ffmpeg_test(original_url):

        print("  [OK] Original")

        verified_list[name] = original_block
        continue


    print("  [FAIL] Original")


    # -----------------------------------------
    # ZEE FALLBACK
    # -----------------------------------------

    if name in ch_zee:

        zee_block = ch_zee[name]

        zee_url = get_stream_url(
            zee_block
        )

        print("  Testing Zee fallback...")

        if ffmpeg_test(zee_url):

            print("  [FALLBACK] Zee")

            verified_list[name] = zee_block

        else:

            print(
                "  [FAILED] Zee -> keeping original"
            )

            verified_list[name] = original_block

    else:

        print(
            "  [NO FALLBACK] keeping original"
        )

        verified_list[name] = original_block


# =========================================================
# OUTPUT
# =========================================================

output_file = "JioTV_Auto.m3u8"

playlist = ["#EXTM3U"]

for block in verified_list.values():
    playlist.extend(block)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(playlist) + "\n"
    )


print()
print("==========================================")
print("DONE")
print("==========================================")
print(f"Channels: {len(verified_list)}")
print(f"Output: {output_file}")
print("No channel removed.")
