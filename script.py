import urllib.request

url = "https://game.denver69.fun/Jtv/EiWIY4/Playlist.m3u"

try:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
        content = response.read().decode("utf-8")

    lines = content.splitlines()
    cleaned_lines = []

    for line in lines:
        if "billed-till" in line or "billed-msg" in line:
            continue
        cleaned_lines.append(line)

    with open("channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))

    print("Success! File cleaned.")

except Exception as e:
    print(f"Error: {e}")
