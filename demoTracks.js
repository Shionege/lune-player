/**
 * demoTracks.js - Synthetic Audio & Cosmic Cover Generator for instant Dribbble demo testing.
 */

export async function generateDemoTracks() {
  const demoList = [
    { title: "This World [E]", artist: "Nora Van Elken", album: "Energetic Music", freq: 440, explicit: true, color1: "#1d1145", color2: "#ff2d55" },
    { title: "A Head Full of Dreams", artist: "Coldplay", album: "Energetic Music", freq: 523.25, explicit: false, color1: "#2b1055", color2: "#7597de" },
    { title: "No Tears Left To Cry", artist: "Ariana Grande", album: "Energetic Music", freq: 349.23, explicit: false, color1: "#4a1231", color2: "#f68084" },
    { title: "Parachutes", artist: "Coldplay", album: "Parachutes", freq: 392.00, explicit: false, color1: "#122a45", color2: "#37ecba" },
    { title: "The Scientist", artist: "Coldplay", album: "A Rush of Blood", freq: 261.63, explicit: false, color1: "#0a192f", color2: "#5e5ce6" },
    { title: "Adventure Of A Lifetime", artist: "Coldplay", album: "A Head Full of Dreams", freq: 440.00, explicit: false, color1: "#3c1053", color2: "#ad5389" },
    { title: "Yellow", artist: "Coldplay", album: "Parachutes", freq: 329.63, explicit: false, color1: "#432c0d", color2: "#f7b731" },
  ];

  const results = [];

  for (let i = 0; i < demoList.length; i++) {
    const spec = demoList[i];
    const audioBlob = createInstantWavBlob(spec.freq, 2.5);
    const coverBlob = await createCosmicCoverArtBlob(spec.title, spec.artist, spec.color1, spec.color2);

    results.push({
      id: 'demo_' + Date.now() + '_' + i,
      title: spec.title,
      artist: spec.artist,
      album: spec.album,
      duration: 162,
      explicit: spec.explicit,
      audioBlob,
      coverBlob,
      isFavorite: i === 0,
      dateAdded: Date.now() - (i * 100000),
    });
  }

  return results;
}

/**
 * Instant 1ms WAV Audio Blob Generator
 */
function createInstantWavBlob(freq = 440, durationSec = 2.5) {
  const sampleRate = 22050;
  const numSamples = Math.floor(sampleRate * durationSec);
  const dataSize = numSamples * 2;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);

  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + dataSize, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // Mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, 'data');
  view.setUint32(40, dataSize, true);

  let offset = 44;
  for (let i = 0; i < numSamples; i++) {
    const t = i / sampleRate;
    const sample = Math.sin(2 * Math.PI * freq * t) * 0.3;
    const intSample = Math.max(-32768, Math.min(32767, Math.floor(sample * 32767)));
    view.setInt16(offset, intSample, true);
    offset += 2;
  }

  return new Blob([buffer], { type: 'audio/wav' });
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

/**
 * Creates rich Cosmic Planet Starburst artwork matching Dribbble inspiration
 */
function createCosmicCoverArtBlob(title, artist, color1, color2) {
  return new Promise((resolve) => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 500;
      canvas.height = 500;
      const ctx = canvas.getContext('2d');

      // Gradient Deep Universe Background
      const grad = ctx.createRadialGradient(250, 250, 20, 250, 250, 350);
      grad.addColorStop(0, color2);
      grad.addColorStop(0.6, color1);
      grad.addColorStop(1, '#050507');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 500, 500);

      // Cosmic Rays / Starburst Lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
      ctx.lineWidth = 1.5;
      for (let i = 0; i < 48; i++) {
        const angle = (i * Math.PI) / 24;
        const r1 = 110 + Math.random() * 20;
        const r2 = 230 + Math.random() * 20;
        ctx.beginPath();
        ctx.moveTo(250 + Math.cos(angle) * r1, 250 + Math.sin(angle) * r1);
        ctx.lineTo(250 + Math.cos(angle) * r2, 250 + Math.sin(angle) * r2);
        ctx.stroke();
      }

      // Outer Neon Ring
      ctx.strokeStyle = 'rgba(166, 192, 254, 0.8)';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(250, 250, 95, 0, Math.PI * 2);
      ctx.stroke();

      // Blue Cosmic Planet Center
      const planetGrad = ctx.createRadialGradient(220, 220, 10, 250, 250, 90);
      planetGrad.addColorStop(0, '#a6c0fe');
      planetGrad.addColorStop(0.5, '#37ecba');
      planetGrad.addColorStop(1, '#050507');
      ctx.fillStyle = planetGrad;
      ctx.beginPath();
      ctx.arc(250, 250, 85, 0, Math.PI * 2);
      ctx.fill();

      // Planet Texture Swirl
      ctx.fillStyle = '#050507';
      ctx.beginPath();
      ctx.arc(250, 250, 45, 0, Math.PI * 2);
      ctx.fill();

      // Title & Artist Label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 24px -apple-system, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText((title || '').replace(/\[e\]/gi, '').trim(), 250, 420);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
      ctx.font = '15px -apple-system, sans-serif';
      ctx.fillText((artist || '').toUpperCase(), 250, 445);

      canvas.toBlob((blob) => resolve(blob), 'image/png');
    } catch (e) {
      resolve(null);
    }
  });
}
