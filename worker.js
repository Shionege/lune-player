/**
 * Lune Player - Cloudflare Worker Audio Relay (v82.0.0)
 * 100% CORS-Free Full-Length Audio Search, Multi-Source Version Picker, Streaming & Downloading Relay
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Range',
  'Access-Control-Expose-Headers': 'Content-Length, Content-Type, Content-Range'
};

let scClientIdCache = 'TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my';

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const pathname = url.pathname;

    try {
      if (pathname === '/search' || pathname === '/search/') {
        const query = url.searchParams.get('q') || 'Indonesia Top Hits';
        const results = await searchAudio(query);
        return new Response(JSON.stringify({ status: true, results }), {
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
        });
      }

      if (pathname === '/sources' || pathname === '/sources/') {
        const query = url.searchParams.get('q') || '';
        const sources = await fetchAudioSources(query, url.origin);
        return new Response(JSON.stringify({ status: true, sources }), {
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
        });
      }

      if (pathname === '/audio' || pathname === '/audio/') {
        const audioRes = await streamAudio(url, request);
        return audioRes;
      }

      // Root info page
      return new Response(JSON.stringify({
        app: 'Lune Player Audio Relay',
        version: 'v96.0.0',
        status: 'Active',
        endpoints: ['/search?q=query', '/sources?q=query', '/audio?q=query']
      }), {
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    } catch (err) {
      return new Response(JSON.stringify({ status: false, error: err.message }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }
  }
};

async function searchAudio(query) {
  // Primary Provider: Official iTunes Search API for 100% Accurate Song Metadata & 600x600 Artwork
  try {
    const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=30`);
    if (res.ok) {
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        return data.results.map(item => ({
          id: `itunes_${item.trackId}`,
          title: item.trackName,
          artist: item.artistName || 'Various Artists',
          album: item.collectionName || 'Single',
          duration: Math.round((item.trackTimeMillis || 180000) / 1000),
          thumbnail: item.artworkUrl100 ? item.artworkUrl100.replace('100x100bb', '600x600bb') : item.artworkUrl60,
          searchTerm: `${item.artistName} - ${item.trackName}`
        }));
      }
    }
  } catch (e) {}

  return [];
}

async function getSoundCloudClientId() {
  if (scClientIdCache) return scClientIdCache;
  try {
    const res = await fetch('https://soundcloud.com', {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    if (res.ok) {
      const html = await res.text();
      const jsMatches = [...html.matchAll(/src="(https:\/\/a-v2\.sndcdn\.com\/assets\/[^"]+\.js)"/g)];
      for (const m of jsMatches.reverse().slice(0, 3)) {
        const jres = await fetch(m[1]);
        if (jres.ok) {
          const jtext = await jres.text();
          const cids = jtext.match(/client_id[:=]"([a-zA-Z0-9]{32})"/);
          if (cids) {
            scClientIdCache = cids[1];
            return scClientIdCache;
          }
        }
      }
    }
  } catch (e) {}
  return 'TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my';
}

async function fetchAudioSources(query, workerOrigin = '') {
  const cleanQ = query.replace(/^itunes_\d+\s*/, '').replace(/[-_]/g, ' ').trim();
  if (!cleanQ) return [];

  // Step 0: Cross-reference Deezer Official Studio Metadata for exact track duration
  let officialTargetDur = 0;
  let officialArtistName = '';
  let officialTrackName = '';
  try {
    const dRes = await fetch(`https://api.deezer.com/search?q=${encodeURIComponent(cleanQ)}`);
    if (dRes.ok) {
      const dData = await dRes.json();
      if (dData.data && dData.data.length > 0) {
        const top = dData.data[0];
        officialTargetDur = top.duration || 0;
        officialArtistName = top.artist?.name || '';
        officialTrackName = top.title || '';
      }
    }
  } catch (e) {}

  const sources = [];
  const bannedKeywords = [
    'cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', 
    '8d', 'nightcore', 'daycore', 'speed up', 'sped up', 'sped', 'tribute', 
    'mashup', 'edit', 'flip', 'bootleg', 'piano', 'originally perfomed', 
    'dj', 'breakbeat', 'funk', 'phonk', 'jedag', 'jedug', 'jj', 
    'tiktok', 'club mix', 'remixer', 'bass boost', 'boosted', 'house mix'
  ];

  // Tag verified record labels
  const officialLabels = [
    'sony music', 'warner music', 'universal music', 'vevo', 'topic', 'official',
    'maksi music', 'denny caknan', 'coldplay', 'ed sheeran', 'ariana grande',
    '35 production', 'musica studio', 'aquarius musikindo', 'trinity optima', 'nagaswara', 'vocal'
  ];

  // 1. Fetch SoundCloud Candidates
  try {
    const cid = await getSoundCloudClientId();
    const scApi = `https://api-v2.soundcloud.com/search/tracks?q=${encodeURIComponent(cleanQ)}&client_id=${cid}&limit=15`;
    const scRes = await fetch(scApi, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    if (scRes.ok) {
      const scData = await scRes.json();
      const collection = scData.collection || [];
      for (const tr of collection) {
        if (tr.duration && tr.duration > 90000) {
          const durSec = Math.round(tr.duration / 1000);
          const minutes = Math.floor(durSec / 60);
          const seconds = durSec % 60;
          const durFormatted = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
          
          const media = tr.media?.transcodings || [];
          const prog = media.find(m => m.format?.protocol === 'progressive');
          if (prog) {
            const tTitle = (tr.title || '').toLowerCase();
            const uName = (tr.user?.username || '').toLowerCase();
            const isBanned = bannedKeywords.some(b => tTitle.includes(b));
            const durDiff = officialTargetDur > 0 ? Math.abs(durSec - officialTargetDur) : 999;
            const isOfficialLabel = officialLabels.some(l => uName.includes(l) || tTitle.includes(l));
            
            let tag = 'Studio Master';
            let priorityScore = 50;

            if (isOfficialLabel && !isBanned) {
              tag = '⭐ Publisher Resmi Label (Official Label)';
              priorityScore = 150 - durDiff;
            } else if (!isBanned && (durDiff <= 10)) {
              tag = 'Rekaman Studio Original (Studio Master)';
              priorityScore = 100 - durDiff;
            } else if (tTitle.includes('official') || tTitle.includes('original')) {
              tag = 'Official Audio';
              priorityScore = 80;
            } else if (tTitle.includes('acoustic')) {
              tag = 'Acoustic';
              priorityScore = 30;
            } else if (tTitle.includes('remix')) {
              tag = 'Remix';
              priorityScore = 20;
            } else if (tTitle.includes('live')) {
              tag = 'Live Version';
              priorityScore = 25;
            } else if (tTitle.includes('slowed') || tTitle.includes('reverb')) {
              tag = 'Slowed & Reverb';
              priorityScore = 10;
            } else if (tTitle.includes('cover')) {
              tag = 'Cover Version';
              priorityScore = 15;
            }

            sources.push({
              id: `sc_${tr.id}`,
              title: tr.title,
              uploader: tr.user?.username || 'SoundCloud Artist',
              duration: durFormatted,
              durationSec: durSec,
              provider: 'SoundCloud CDN',
              tag: tag,
              isOfficialLabel: isOfficialLabel,
              priorityScore: priorityScore,
              streamUrl: `${workerOrigin}/audio?sc_prog=${encodeURIComponent(prog.url)}&cid=${cid}`
            });
          }
        }
      }
    }
  } catch (e) {}

  // 2. Provider: JioSaavn 320kbps Official Studio Audio Engine
  try {
    const sRes = await fetch(`https://saavn.dev/api/search/songs?query=${encodeURIComponent(cleanQ)}`);
    if (sRes.ok) {
      const sData = await sRes.json();
      const songs = sData.data?.results || sData.results || [];
      for (const s of songs.slice(0, 6)) {
        const dUrls = s.downloadUrl || [];
        const hqUrlObj = Array.isArray(dUrls) && dUrls.length > 0 ? dUrls[dUrls.length - 1] : null;
        const streamUrl = hqUrlObj ? hqUrlObj.url : (typeof s.media_url === 'string' ? s.media_url : null);
        if (streamUrl) {
          const sArtist = s.primaryArtists || s.singers || 'Official Artist';
          const sTitle = s.name || s.title || cleanQ;
          const sTitleLower = sTitle.toLowerCase();
          const sArtistLower = sArtist.toLowerCase();
          
          const isBanned = bannedKeywords.some(b => sTitleLower.includes(b) || sArtistLower.includes(b) || sTitleLower.includes('originally perfomed') || sTitleLower.includes('piano'));
          const durSec = s.duration ? parseInt(s.duration, 10) : 210;
          const minutes = Math.floor(durSec / 60);
          const seconds = durSec % 60;
          const durFormatted = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

          let tag = '⭐ Publisher Resmi Label (JioSaavn Studio 320k)';
          let priorityScore = 200;
          let isOfficial = true;

          if (isBanned) {
            tag = 'Cover / Karaoke Version';
            priorityScore = 15;
            isOfficial = false;
          }

          sources.push({
            id: `saavn_${s.id || Math.random()}`,
            title: sTitle,
            uploader: `${sArtist} ${isOfficial ? '(Official Label)' : '(Karaoke/Cover)'}`,
            duration: durFormatted,
            durationSec: durSec,
            provider: 'JioSaavn 320kbps Network',
            tag: tag,
            isOfficialLabel: isOfficial,
            priorityScore: priorityScore,
            streamUrl: `${workerOrigin}/audio?direct_url=${encodeURIComponent(streamUrl)}`
          });
        }
      }
    }
  } catch (e) {}

  // 3. Provider: Jamendo Music HQ
  try {
    const jRes = await fetch(`https://api.jamendo.com/v3.0/tracks/?client_id=56d306e9&format=json&limit=4&namesearch=${encodeURIComponent(cleanQ)}`);
    if (jRes.ok) {
      const jData = await jRes.json();
      const tracks = jData.results || [];
      for (const jtr of tracks) {
        if (jtr.audio) {
          const durSec = jtr.duration || 180;
          const minutes = Math.floor(durSec / 60);
          const seconds = durSec % 60;
          const durFormatted = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
          sources.push({
            id: `jamendo_${jtr.id}`,
            title: jtr.name,
            uploader: `${jtr.artist_name} (Jamendo)`,
            duration: durFormatted,
            durationSec: durSec,
            provider: 'Jamendo HQ Network',
            tag: 'Jamendo HQ Studio MP3',
            priorityScore: 90,
            streamUrl: `${workerOrigin}/audio?direct_url=${encodeURIComponent(jtr.audio)}`
          });
        }
      }
    }
  } catch (e) {}

  // 4. Provider: Internet Archive.org Candidates
  try {
    const aRes = await fetch(`https://archive.org/advancedsearch.php?q=%28${encodeURIComponent(cleanQ)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=5&output=json`);
    if (aRes.ok) {
      const aData = await aRes.json();
      const docs = aData.response?.docs || [];
      for (const d of docs) {
        sources.push({
          id: `archive_${d.identifier}`,
          title: d.title || cleanQ,
          uploader: d.creator || 'Archive.org',
          duration: d.duration || 'Full',
          durationSec: 200,
          provider: 'Internet Archive Vault',
          tag: 'Archive MP3',
          priorityScore: 40,
          streamUrl: `${workerOrigin}/audio?q=archive_${d.identifier}`
        });
      }
    }
  } catch (e) {}

  // 5. Provider: YouTube Music Proxy Stream Engine
  const ytSearchMirrors = [
    `https://invidious.flokinet.to/api/v1/search?q=${encodeURIComponent(cleanQ)}&type=video`,
    `https://inv.tux.pizza/api/v1/search?q=${encodeURIComponent(cleanQ)}&type=video`,
    `https://vid.puffyan.us/api/v1/search?q=${encodeURIComponent(cleanQ)}&type=video`
  ];
  for (const sUrl of ytSearchMirrors) {
    try {
      const invRes = await fetch(sUrl);
      if (invRes.ok) {
        const invData = await invRes.json();
        if (Array.isArray(invData) && invData.length > 0) {
          for (const v of invData.slice(0, 4)) {
            if (v.videoId && v.lengthSeconds > 60 && v.lengthSeconds < 1200) {
              const vTitle = v.title || '';
              const vTitleLower = vTitle.toLowerCase();
              const isBanned = bannedKeywords.some(b => vTitleLower.includes(b));
              if (!isBanned) {
                const durSec = v.lengthSeconds;
                const minutes = Math.floor(durSec / 60);
                const seconds = durSec % 60;
                const durFormatted = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                
                sources.push({
                  id: `yt_${v.videoId}`,
                  title: vTitle,
                  uploader: `${v.author || 'YouTube Music'} (Official Stream)`,
                  duration: durFormatted,
                  durationSec: durSec,
                  provider: 'YouTube Music Proxy',
                  tag: '⭐ YouTube Audio Master',
                  isOfficialLabel: true,
                  priorityScore: 190,
                  streamUrl: `${workerOrigin}/audio?yt_id=${v.videoId}`
                });
              }
            }
          }
          if (sources.some(s => s.provider === 'YouTube Music Proxy')) break;
        }
      }
    } catch (e) {}
  }

  // Sort sources by priorityScore descending so Official 320k / YouTube Masters are always #1!
  sources.sort((a, b) => b.priorityScore - a.priorityScore);

  return sources;
}

async function streamAudio(urlObj, originalRequest) {
  const query = urlObj.searchParams.get('q') || urlObj.searchParams.get('id') || '';
  const scProg = urlObj.searchParams.get('sc_prog');
  const directUrl = urlObj.searchParams.get('direct_url');
  const ytId = urlObj.searchParams.get('yt_id');
  const scCid = urlObj.searchParams.get('cid') || await getSoundCloudClientId();

  // If direct audio URL is requested (e.g. JioSaavn 320k or Jamendo HQ)
  if (directUrl) {
    return await fetchAndProxyAudio(directUrl, originalRequest);
  }

  // If specific YouTube Music video ID is requested
  if (ytId) {
    const mirrorUrls = [
      `https://invidious.flokinet.to/api/v1/videos/${ytId}`,
      `https://inv.tux.pizza/api/v1/videos/${ytId}`,
      `https://vid.puffyan.us/api/v1/videos/${ytId}`,
      `https://invidious.drgns.space/api/v1/videos/${ytId}`
    ];
    for (const mUrl of mirrorUrls) {
      try {
        const mRes = await fetch(mUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } });
        if (mRes.ok) {
          const mData = await mRes.json();
          const audioStream = mData.adaptiveFormats?.find(f => f.type?.includes('audio') || f.mimeType?.includes('audio')) ||
                              mData.audioStreams?.[0];
          if (audioStream?.url) {
            return await fetchAndProxyAudio(audioStream.url, originalRequest);
          }
        }
      } catch (e) {}
    }
  }

  // If specific SoundCloud progressive stream URL is requested
  if (scProg) {
    try {
      const streamApi = `${scProg}?client_id=${scCid}`;
      const sRes = await fetch(streamApi, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
      });
      if (sRes.ok) {
        const sData = await sRes.json();
        if (sData.url) {
          return await fetchAndProxyAudio(sData.url, originalRequest);
        }
      }
    } catch (e) {}
  }

  // If request is from Archive.org identifier
  if (query.startsWith('archive_')) {
    const ident = query.replace('archive_', '');
    try {
      const metaRes = await fetch(`https://archive.org/metadata/${ident}`);
      if (metaRes.ok) {
        const meta = await metaRes.json();
        const files = meta.files || [];
        const mp3s = files.filter(f => f.name && f.name.endsWith('.mp3'));
        if (mp3s.length > 0) {
          const directUrl = `https://archive.org/download/${ident}/${encodeURIComponent(mp3s[0].name)}`;
          return await fetchAndProxyAudio(directUrl, originalRequest);
        }
      }
    } catch (e) {}
    return await fetchAndProxyAudio(`https://archive.org/download/${ident}/${ident}.mp3`, originalRequest);
  }

  const cleanQ = query.replace(/^itunes_\d+\s*/, '').replace(/[-_]/g, ' ').trim();
  if (!cleanQ) {
    return new Response(JSON.stringify({ error: 'Query parameter is empty' }), {
      status: 400,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
    });
  }

  // Primary Engine: SoundCloud Full-Length Audio Stream Extractor (Duration > 100s + Strict Original Filter)
  try {
    const cid = await getSoundCloudClientId();
    const scApi = `https://api-v2.soundcloud.com/search/tracks?q=${encodeURIComponent(cleanQ)}&client_id=${cid}&limit=20`;
    const scRes = await fetch(scApi, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    if (scRes.ok) {
      const scData = await scRes.json();
      const tracks = scData.collection || [];
      
      const bannedKeywords = [
        'cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', 
        '8d', 'nightcore', 'daycore', 'speed up', 'sped up', 'sped', 'tribute', 
        'mashup', 'edit', 'flip', 'bootleg', 'piano', 'originally perfomed', 
        'dj', 'breakbeat', 'funk', 'phonk', 'jedag', 'jedug', 'jj', 
        'tiktok', 'club mix', 'remixer', 'bass boost', 'boosted', 'house mix'
      ];
      
      const originalTracks = [];
      const fallbackTracks = [];

      for (const tr of tracks) {
        if (tr.duration && tr.duration > 100000) {
          const tTitle = (tr.title || '').toLowerCase();
          const isBanned = bannedKeywords.some(b => tTitle.includes(b));
          if (!isBanned) {
            originalTracks.push(tr);
          } else {
            fallbackTracks.push(tr);
          }
        }
      }

      const targetList = originalTracks.length > 0 ? originalTracks : fallbackTracks;

      for (const tr of targetList) {
        const media = tr.media?.transcodings || [];
        const prog = media.find(m => m.format?.protocol === 'progressive');
        if (prog) {
          const streamApi = `${prog.url}?client_id=${cid}`;
          const sRes = await fetch(streamApi, {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
          });
          if (sRes.ok) {
            const sData = await sRes.json();
            if (sData.url) {
              return await fetchAndProxyAudio(sData.url, originalRequest);
            }
          }
        }
      }
    }
  } catch (e) {}

  // 2. Secondary Engine: Archive.org Exact Title Search
  try {
    const aRes = await fetch(`https://archive.org/advancedsearch.php?q=%28${encodeURIComponent(cleanQ)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=5&output=json`);
    if (aRes.ok) {
      const aData = await aRes.json();
      const docs = aData.response?.docs || [];
      for (const d of docs) {
        const metaRes = await fetch(`https://archive.org/metadata/${d.identifier}`);
        if (metaRes.ok) {
          const meta = await metaRes.json();
          const mp3s = (meta.files || []).filter(f => f.name && f.name.endsWith('.mp3'));
          if (mp3s.length > 0) {
            const streamUrl = `https://archive.org/download/${d.identifier}/${encodeURIComponent(mp3s[0].name)}`;
            return await fetchAndProxyAudio(streamUrl, originalRequest);
          }
        }
      }
    }
  } catch (e) {}

  return new Response(JSON.stringify({ error: 'Full length audio stream not found' }), {
    status: 404,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
  });
}

async function fetchAndProxyAudio(audioUrl, originalRequest) {
  const reqHeaders = new Headers();
  const range = originalRequest.headers.get('Range');
  if (range) reqHeaders.set('Range', range);
  reqHeaders.set('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');

  const response = await fetch(audioUrl, { headers: reqHeaders });

  const resHeaders = new Headers(CORS_HEADERS);
  const passHeaders = ['content-type', 'content-length', 'content-range', 'accept-ranges'];
  for (const h of passHeaders) {
    if (response.headers.has(h)) {
      resHeaders.set(h, response.headers.get(h));
    }
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: resHeaders
  });
}
