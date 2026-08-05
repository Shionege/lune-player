const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const url = require('url');

const PORT = 8080;
const PUBLIC_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.webm': 'audio/webm'
};

const server = http.createServer((req, res) => {
  // Enable CORS headers for all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // --- API 1: Fetch Playlist Metadata via yt-dlp ---
  if (pathname === '/api/yt-metadata') {
    const playlistUrl = parsedUrl.query.url;
    if (!playlistUrl) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Missing url parameter' }));
      return;
    }

    console.log(`[SERVER] Extracting metadata for: ${playlistUrl}`);
    // Extract playlist metadata via yt-dlp JSON dump
    const cmd = `yt-dlp --flat-playlist -J "${playlistUrl}"`;
    exec(cmd, { maxBuffer: 10 * 1024 * 1024 }, (err, stdout, stderr) => {
      if (err || !stdout) {
        console.error('[SERVER] Metadata error:', err || stderr);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to extract metadata' }));
        return;
      }

      try {
        const data = JSON.parse(stdout);
        const entries = data.entries || [data];
        const tracks = entries.map(e => ({
          id: e.id,
          title: e.title || 'Unknown Title',
          artist: e.uploader || e.artist || e.channel || 'YouTube Artist',
          duration: e.duration || 180,
          thumbnail: e.thumbnails && e.thumbnails.length > 0 ? e.thumbnails[e.thumbnails.length - 1].url : `https://i.ytimg.com/vi/${e.id}/hqdefault.jpg`
        })).filter(t => t.id);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          title: data.title || 'YouTube Playlist',
          count: tracks.length,
          tracks: tracks
        }));
      } catch (e) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // --- API 2: Direct Audio Stream via yt-dlp ---
  if (pathname === '/api/yt-stream') {
    const videoId = parsedUrl.query.id;
    if (!videoId) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Missing id parameter' }));
      return;
    }

    console.log(`[SERVER] Streaming exact audio for video: ${videoId}`);
    const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;

    // Get direct audio stream URL via yt-dlp -g -f bestaudio
    const cmd = `yt-dlp -g -f bestaudio "${videoUrl}"`;
    exec(cmd, (err, stdout, stderr) => {
      if (err || !stdout.trim()) {
        console.error('[SERVER] Stream URL error:', err || stderr);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to extract audio stream URL' }));
        return;
      }

      const streamUrl = stdout.trim().split('\n')[0];
      console.log(`[SERVER] Pipe streaming audio from: ${streamUrl.substring(0, 70)}...`);

      res.writeHead(200, {
        'Content-Type': 'audio/mpeg',
        'Cache-Control': 'no-cache'
      });

      // Proxy stream directly to browser client
      const fetchModule = streamUrl.startsWith('https') ? require('https') : require('http');
      fetchModule.get(streamUrl, (streamRes) => {
        streamRes.pipe(res);
      }).on('error', (e) => {
        console.error('[SERVER] Stream proxying error:', e.message);
        if (!res.headersSent) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: e.message }));
        }
      });
    });
    return;
  }

  // --- Static File Handler ---
  let filePath = path.join(PUBLIC_DIR, pathname === '/' ? 'index.html' : pathname);
  const extname = String(path.extname(filePath)).toLowerCase();
  const contentType = MIME_TYPES[extname] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>', 'utf-8');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`, 'utf-8');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.listen(PORT, () => {
  console.log(`\n==================================================`);
  console.log(`🚀 Lune Player Native Downloader Server Running!`);
  console.log(`URL: http://localhost:${PORT}`);
  console.log(`==================================================\n`);
});
