import re
import requests

# =========================================================
# PLAYLIST URLS
# =========================================================

url_1173 = "https://raw.githubusercontent.com/Diljan707/Automated-/refs/heads/main/JioTV_Auto.m3u"
url_958 = "https://jhs-channels.rtxcric.workers.dev/playlist.m3u"
url_zee = "https://raw.githubusercontent.com/Sflex0719/STBPLUS/refs/heads/main/Zio.m3u"
url_sony = "https://raw.githubusercontent.com/Diljan707/sony-hls/refs/heads/main/all_sony_live_tokens.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================================================
# HTTP STATUS WHICH SHOULD TRIGGER FALLBACK
# =========================================================

ERROR_STATUSES = {
    400,
    401,
    402,
    403,
    404,
    405,
    408,
    410,
    429,
    500,
    501,
    502,
    503,
    504
}

# 302 is handled separately because redirect is disabled.
ERROR_STATUSES.add(302)


# =========================================================
# FETCH PLAYLIST
# =========================================================

def fetch_playlist(url):

    try:
        r = requests.get(
            url,
            timeout=15,
            headers=HEADERS
        )

        if r.status_code == 200:
            print(f"[PLAYLIST OK] {url}")
            return r.text.splitlines()

        print(
            f"[PLAYLIST ERROR] "
            f"{url} -> {r.status_code}"
        )

        return []

    except Exception as e:

        print(
            f"[PLAYLIST ERROR] "
            f"{url} -> {e}"
        )

        return []


lines_1173 = fetch_playlist(url_1173)
lines_958 = fetch_playlist(url_958)
lines_zee = fetch_playlist(url_zee)
lines_sony = fetch_playlist(url_sony)


# =========================================================
# PARSE CHANNELS
# =========================================================

def parse_channels(lines):

    channels = {}

    i = 0

    while i < len(lines):

        if lines[i].startswith("#EXTINF"):

            extinf = lines[i]

            # Remove group-title
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

            name = (
                extinf
                .split(",")[-1]
                .strip()
                .lower()
            )

            channels[name] = block

        else:

            i += 1

    return channels


ch_1173 = parse_channels(lines_1173)
ch_958 = parse_channels(lines_958)
ch_zee = parse_channels(lines_zee)
ch_sony = parse_channels(lines_sony)


# =========================================================
# 1. 1173 CHANNELS
# REMOVE STAR SPORTS / ZEE / SONY PAL
# =========================================================

final_list = {}

for n, b in ch_1173.items():

    if (
        "star sports" in n
        or "zee" in n
        or "sony pal" in n
    ):
        continue

    final_list[n] = b


# =========================================================
# 2. ADD SELECTED STAR SPORTS DIGITAL
# =========================================================

target_star_channels = {
    "star sports 1 digital",
    "star sports 1 hindi digital",
    "star sports 2 digital",
    "star sports 2 hindi digital",
    "star sports 3 digital",
    "star sports khel digital"
}

for n, b in ch_958.items():

    if any(
        target in n
        for target in target_star_channels
    ):
        final_list[n] = b


# =========================================================
# 3. ADD ZEE CHANNELS
# =========================================================

for n, b in ch_zee.items():

    if "zee" in n:
        final_list[n] = b


# =========================================================
# 4. ADD SONY PAL + SONY TEN 1-6
# =========================================================

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

    if any(
        keyword in n
        for keyword in target_sony_keywords
    ):
        final_list[n] = b


# =========================================================
# GET STREAM URL FROM CHANNEL BLOCK
# =========================================================

def get_stream_url(block):

    for line in block:

        line = line.strip()

        if (
            line
            and not line.startswith("#")
        ):
            return line

    return ""


# =========================================================
# CHECK STREAM
# =========================================================

def check_stream(url):

    if not url:
        return False, None

    try:

        # ---------------------------------------------
        # HEAD
        # Redirects disabled
        # ---------------------------------------------

        res = requests.head(
            url,
            timeout=5,
            headers=HEADERS,
            allow_redirects=False
        )

        status = res.status_code

        res.close()

        # Clear HTTP errors
        if status in ERROR_STATUSES:
            return False, status

        # 200 = working
        if status == 200:
            return True, status

        # ---------------------------------------------
        # Some servers don't support HEAD
        # Try GET
        # ---------------------------------------------

        res = requests.get(
            url,
            timeout=5,
            stream=True,
            headers=HEADERS,
            allow_redirects=False
        )

        status = res.status_code

        if status in ERROR_STATUSES:

            res.close()

            return False, status

        if status == 200:

            res.close()

            return True, status

        res.close()

        # ---------------------------------------------
        # IMPORTANT:
        # 451 is NOT treated as broken.
        # Unknown statuses are also kept.
        # ---------------------------------------------

        return True, status

    except Exception as e:

        print(
            f"[CONNECTION ERROR] {e}"
        )

        return False, None


# =========================================================
# SMART FALLBACK
#
# ORIGINAL FAILED
#       ↓
# ZEE EXISTS?
#       ↓
# CHECK ZEE
#       ↓
# ZEE WORKING -> USE ZEE
# ZEE FAILED  -> KEEP ORIGINAL
# =========================================================

verified_list = {}

for n, original_block in final_list.items():

    original_url = get_stream_url(
        original_block
    )

    original_working, original_status = check_stream(
        original_url
    )

    # -----------------------------------------------------
    # ORIGINAL WORKING
    # -----------------------------------------------------

    if original_working:

        print(
            f"[OK/KEEP] {n} | "
            f"Status: {original_status}"
        )

        verified_list[n] = original_block

        continue


    # -----------------------------------------------------
    # ORIGINAL FAILED
    # -----------------------------------------------------

    print(
        f"[ORIGINAL FAILED] {n} | "
        f"Status: {original_status}"
    )


    # -----------------------------------------------------
    # CHECK ZEE FALLBACK
    # -----------------------------------------------------

    if n in ch_zee:

        zee_block = ch_zee[n]

        zee_url = get_stream_url(
            zee_block
        )

        zee_working, zee_status = check_stream(
            zee_url
        )


        # ---------------------------------------------
        # ZEE WORKING
        # ---------------------------------------------

        if zee_working:

            print(
                f"[ZEE FALLBACK OK] {n} | "
                f"Zee Status: {zee_status}"
            )

            verified_list[n] = zee_block


        # ---------------------------------------------
        # ZEE ALSO FAILED
        # KEEP ORIGINAL
        # ---------------------------------------------

        else:

            print(
                f"[ZEE FAILED] {n} | "
                f"Zee Status: {zee_status} | "
                f"KEEPING ORIGINAL"
            )

            verified_list[n] = original_block


    # -----------------------------------------------------
    # NO ZEE FALLBACK
    # KEEP ORIGINAL
    # -----------------------------------------------------

    else:

        print(
            f"[NO ZEE FALLBACK] {n} | "
            f"Keeping original"
        )

        verified_list[n] = original_block


# =========================================================
# CREATE FINAL M3U
# =========================================================

final_playlist = [
    "#EXTM3U"
]

for block in verified_list.values():

    final_playlist.extend(block)


# =========================================================
# WRITE FILE
# =========================================================

output_file = "JioTV_Auto.m3u8"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(final_playlist)
        + "\n"
    )


# =========================================================
# COMPLETE
# =========================================================

print()
print("==========================================")
print("SUCCESS!")
print("==========================================")
print(
    f"Final playlist: {output_file}"
)
print(
    f"Total channels: {len(verified_list)}"
)
print("No channel was removed.")
print("==========================================")
