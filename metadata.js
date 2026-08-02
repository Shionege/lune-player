/**
 * metadata.js - ID3 Tag Extractor & Fallback Metadata Parser
 * Uses jsmediatags (if available via CDN/window) or fallback filename parsing.
 */

export async function extractMetadata(file) {
  const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
  let title = fileNameWithoutExt;
  let artist = "Unknown Artist";
  let album = "Single";
  let explicit = false;
  let coverBlob = null;

  // Check explicit tag in filename e.g., "Song Name [E]" or "Song Name (Explicit)"
  if (/\[e\]|\(explicit\)/i.test(fileNameWithoutExt)) {
    explicit = true;
    title = title.replace(/\[e\]|\(explicit\)/gi, "").trim();
  }

  // Attempt to parse Artist - Title format from filename
  if (title.includes(" - ")) {
    const parts = title.split(" - ");
    artist = parts[0].trim();
    title = parts.slice(1).join(" - ").trim();
  }

  let duration = 0;

  // Try extracting ID3 tags using jsmediatags if available
  if (window.jsmediatags) {
    try {
      const tags = await new Promise((resolve) => {
        window.jsmediatags.read(file, {
          onSuccess: (tag) => resolve(tag.tags),
          onError: (error) => {
            console.warn("jsmediatags failed, using fallback:", error);
            resolve(null);
          },
        });
      });

      if (tags) {
        if (tags.title && tags.title.trim()) title = tags.title.trim();
        if (tags.artist && tags.artist.trim()) artist = tags.artist.trim();
        if (tags.album && tags.album.trim()) album = tags.album.trim();

        // Extract Picture
        if (tags.picture) {
          const { data, format } = tags.picture;
          let byteArray = new Uint8Array(data);
          coverBlob = new Blob([byteArray], { type: format || "image/jpeg" });
        }
      }
    } catch (e) {
      console.warn("Error running jsmediatags:", e);
    }
  }

  // Get duration using Audio element
  try {
    duration = await getAudioDuration(file);
  } catch (e) {
    console.warn("Could not get duration:", e);
    duration = 180; // default 3 min fallback if unreadable
  }

  const id = 'song_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

  return {
    id,
    title,
    artist,
    album,
    duration,
    explicit,
    audioBlob: file,
    coverBlob,
    isFavorite: false,
    dateAdded: Date.now(),
  };
}

function getAudioDuration(file) {
  return new Promise((resolve) => {
    const audio = new Audio();
    const url = URL.createObjectURL(file);
    audio.src = url;

    audio.onloadedmetadata = () => {
      URL.revokeObjectURL(url);
      resolve(audio.duration || 0);
    };

    audio.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(0);
    };
  });
}
