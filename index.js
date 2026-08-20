const fs = require('fs');

const JSON_URL = "https://raw.githubusercontent.com/drmlive/sliv-live-events/main/sonyliv.json";
const STREAM_PROXY = "https://mini.allinonereborn.site/events/stream_proxy.php?url=";

let DATA = [];

async function buildM3U() {
  try {
    const res = await fetch(JSON_URL);
    const data = await res.json();
    
    DATA = Array.isArray(data) ? data : (data.matches || []);

    let m3u = "#EXTM3U\n";

    DATA.forEach((item, index) => {
      const title = item.event_name || item.name || `Live Event ${index + 1}`;
      const logo = item.src || item.poster || "";
      const group = item.event_category || "SonyLIV";
      
      const rawUrl = item.url || item.contentId || ""; 
      const streamUrl = STREAM_PROXY + encodeURIComponent(rawUrl);

      m3u += `#EXTINF:-1 tvg-logo="${logo}" group-title="${group}",${title}\n`;
      m3u += `${streamUrl}\n`;
    });

    // M3U ਫਾਈਲ ਨੂੰ ਰਿਪੋਜ਼ਟਰੀ ਵਿੱਚ save ਕਰਨਾ
    fs.writeFileSync('playlist.m3u', m3u);
    console.log("M3U playlist successfully generated!");

  } catch (err) {
    console.error("ਗਲਤੀ ਆਈ:", err);
  }
}

buildM3U();
