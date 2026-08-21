import os
import re

file_path = "channels.m3u"

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found!")
    exit()

try:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    
    for line in lines:
        # ਜੇ ਲਾਈਨ ਚੈਨਲ ਇਨਫੋ (#EXTINF) ਵਾਲੀ ਹੈ
        if line.startswith("#EXTINF"):
            # group-title ਵਾਲਾ ਹਿੱਸਾ regex ਨਾਲ ਹਟਾ ਦਿਓ
            line = re.sub(r' group-title="[^"]*"', '', line)
            # ਫਾਲਤੂ ਸਪੇਸ ਸਾਫ਼ ਕਰੋ
            line = line.replace(' ,', ',')
            cleaned_lines.append(line)
        else:
            # ਬਾਕੀ ਲਾਈਨਾਂ (ਲਿੰਕ ਆਦਿ) ਉਵੇਂ ਹੀ ਰੱਖੋ
            cleaned_lines.append(line)

    # ਸਾਫ਼ ਕੀਤੀ ਹੋਈ ਫ਼ਾਈਲ ਨੂੰ ਵਾਪਸ ਸੇਵ ਕਰੋ
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    print("Success! All categories removed, channels unified.")

except Exception as e:
    print(f"Error: {e}")
                          
