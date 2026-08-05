/**
 * player.js - Audio Player Engine with Web Audio API Equalizer & MediaSession
 * iOS Background Audio Fix: handles AudioContext suspension & visibilitychange
 */

class AudioPlayerEngine {
  constructor() {
    this.audio = new Audio();
    this.audio.setAttribute('playsinline', 'true');
    this.audio.setAttribute('webkit-playsinline', 'true');
    this.audio.setAttribute('x5-playsinline', 'true');
    this.audio.preload = 'auto';
    this.queue = [];
    this.originalQueue = [];
    this.currentIndex = -1;

    this.isPlaying = false;
    this.repeatMode = 'off'; // 'off' | 'all' | 'one'
    this.isShuffle = false;

    this.audioContext = null;
    this.mediaElementSource = null;
    this.eqFilters = [];
    this.eqPresets = {
      flat: [0, 0, 0, 0, 0],
      bass: [6, 4, 0, -2, -4],
      pop: [-1, 2, 4, 2, -1],
      rock: [5, 3, -1, 3, 5],
      vocal: [-2, 0, 4, 3, 0],
    };

    // Callbacks
    this.onTrackChange = null;
    this.onPlayStateChange = null;
    this.onTimeUpdate = null;
    this.onQueueChange = null;

    this.initAudioEvents();
    this.initVisibilityHandler();
  }

  /**
   * iOS Background Audio Fix:
   * When app goes to background, iOS suspends AudioContext.
   * On returning to foreground, resume it so audio keeps playing.
   */
  initVisibilityHandler() {
    const handleStateCheck = async () => {
      if (this.audioContext && this.audioContext.state === 'suspended' && this.isPlaying) {
        try {
          await this.audioContext.resume();
        } catch (e) {}
      }
      if (this.isPlaying && this.audio.paused) {
        try {
          await this.audio.play();
        } catch (e) {}
      }
    };

    document.addEventListener('visibilitychange', handleStateCheck);
    window.addEventListener('pagehide', handleStateCheck);
    window.addEventListener('blur', handleStateCheck);
    window.addEventListener('freeze', handleStateCheck);
    window.addEventListener('resume', handleStateCheck);
  }

  async play() {
    if (this.currentIndex < 0 || this.queue.length === 0) return;
    this.initAudioContext();
    if (this.audioContext && this.audioContext.state === 'suspended') {
      try {
        await this.audioContext.resume();
      } catch (e) {}
    }

    try {
      await this.audio.play();
      this.isPlaying = true;
      this.setupMediaSession();
      if (this.onPlayStateChange) this.onPlayStateChange(true);
      
      // Acquire Web Locks API background lock
      if ('locks' in navigator) {
        navigator.locks.request('lune_player_playback', { mode: 'shared' }, () => {
          return new Promise((resolve) => {
            this.audio.addEventListener('pause', resolve, { once: true });
            this.audio.addEventListener('ended', resolve, { once: true });
          });
        });
      }
    } catch (e) {
      console.warn("Play interrupted / deferred:", e);
      this.isPlaying = false;
      if (this.onPlayStateChange) this.onPlayStateChange(false);
    }
  }

  initAudioContext() {
    if (this.audioContext) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioCtx();
      this.mediaElementSource = this.audioContext.createMediaElementSource(this.audio);
      
      // Create a GainNode to control volume under Web Audio (necessary for iOS/Safari bug)
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = this.audio.volume;

      // Preamp headroom gain node to prevent clipping distortion
      this.preampNode = this.audioContext.createGain();
      this.preampNode.gain.value = 1.0;

      // Anti-distortion Limiter / DynamicsCompressor Node
      this.limiterNode = this.audioContext.createDynamicsCompressor();
      this.limiterNode.threshold.value = -3.0;
      this.limiterNode.knee.value = 6.0;
      this.limiterNode.ratio.value = 12.0;
      this.limiterNode.attack.value = 0.003;
      this.limiterNode.release.value = 0.15;

      // Frequencies for 5-band EQ
      const frequencies = [60, 230, 910, 3600, 14000];
      let lastNode = this.mediaElementSource;

      this.eqFilters = frequencies.map((freq) => {
        const filter = this.audioContext.createBiquadFilter();
        filter.type = 'peaking';
        filter.frequency.value = freq;
        filter.Q.value = 1.0;
        filter.gain.value = 0;
        lastNode.connect(filter);
        lastNode = filter;
        return filter;
      });

      // Route: EQ Filters -> Preamp -> Volume Gain -> Compressor Limiter -> Destination
      lastNode.connect(this.preampNode);
      this.preampNode.connect(this.gainNode);
      this.gainNode.connect(this.limiterNode);
      this.limiterNode.connect(this.audioContext.destination);

      // Auto-resume AudioContext if iOS attempts to suspend it while playing
      this.audioContext.onstatechange = async () => {
        if (this.audioContext && this.audioContext.state === 'suspended' && this.isPlaying) {
          try {
            await this.audioContext.resume();
          } catch (e) {}
        }
      };
    } catch (e) {
      console.warn("Web Audio API equalizer initialization failed:", e);
    }
  }

  updateHeadroom() {
    if (!this.preampNode || !this.audioContext) return;
    const maxBoost = Math.max(0, ...this.eqFilters.map(f => f.gain.value));
    const factor = maxBoost > 0 ? Math.pow(10, -maxBoost / 26) : 1.0;
    try {
      this.preampNode.gain.setValueAtTime(factor, this.audioContext.currentTime);
    } catch (e) {
      this.preampNode.gain.value = factor;
    }
  }

  initAudioEvents() {
    this.audio.addEventListener('play', () => {
      this.isPlaying = true;
      if (this.onPlayStateChange) this.onPlayStateChange(true);
      this.updateMediaSessionState();
    });

    this.audio.addEventListener('pause', () => {
      this.isPlaying = false;
      if (this.onPlayStateChange) this.onPlayStateChange(false);
      this.updateMediaSessionState();
    });

    this.audio.addEventListener('timeupdate', () => {
      if (this.onTimeUpdate) {
        this.onTimeUpdate(this.audio.currentTime, this.audio.duration || 0);
      }
    });

    this.audio.addEventListener('ended', () => {
      this.handleTrackEnded();
    });

    // iOS: Resume AudioContext on user interaction (required by iOS policy)
    this.audio.addEventListener('play', async () => {
      if (this.audioContext && this.audioContext.state === 'suspended') {
        try {
          await this.audioContext.resume();
        } catch (e) {
          console.warn('AudioContext resume on play failed:', e);
        }
      }
    });

    this.setupMediaSession();
  }

  setupMediaSession() {
    if (!('mediaSession' in navigator)) return;

    const actionHandlers = [
      ['play', () => this.play()],
      ['pause', () => this.pause()],
      ['previoustrack', () => this.prev()],
      ['nexttrack', () => this.next()],
      // Unsetting seekto, seekforward, and seekbackward forces iOS Lock Screen & Control Center to render Previous Track and Next Track buttons
      ['seekto', null],
      ['seekforward', null],
      ['seekbackward', null]
    ];

    for (const [action, handler] of actionHandlers) {
      try {
        navigator.mediaSession.setActionHandler(action, handler);
      } catch (e) {
        // Catch unsupported actions gracefully
      }
    }
  }

  updateMediaSessionMetadata(song, coverUrl) {
    if (!('mediaSession' in navigator) || !song) return;

    const cleanTitle = (song.title || 'Unknown Title').replace(/\[e\]/gi, '').trim();
    const artworkSrc = coverUrl || getDefaultCoverUrl(cleanTitle, song.artist);

    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: cleanTitle,
        artist: song.artist || 'Unknown Artist',
        album: song.album || 'Lune Player',
        artwork: [
          { src: artworkSrc, sizes: '96x96', type: 'image/png' },
          { src: artworkSrc, sizes: '128x128', type: 'image/png' },
          { src: artworkSrc, sizes: '192x192', type: 'image/png' },
          { src: artworkSrc, sizes: '256x256', type: 'image/png' },
          { src: artworkSrc, sizes: '384x384', type: 'image/png' },
          { src: artworkSrc, sizes: '512x512', type: 'image/png' },
        ]
      });
    } catch (e) {
      console.warn("MediaMetadata creation error:", e);
    }
  }

  updateMediaSessionState() {
    if ('mediaSession' in navigator) {
      navigator.mediaSession.playbackState = this.isPlaying ? 'playing' : 'paused';
    }
  }

  setQueue(songs, startIndex = 0) {
    this.originalQueue = [...songs];
    if (this.isShuffle) {
      this.queue = this.shuffleArray([...songs]);
    } else {
      this.queue = [...songs];
    }
    this.currentIndex = startIndex >= 0 && startIndex < this.queue.length ? startIndex : 0;
    if (this.onQueueChange) this.onQueueChange(this.queue);
    this.loadCurrentTrack();
  }

  loadCurrentTrack() {
    if (this.currentIndex < 0 || this.currentIndex >= this.queue.length) return;
    const currentSong = this.queue[this.currentIndex];
    if (!currentSong) return;

    if (this.currentObjectUrl) {
      URL.revokeObjectURL(this.currentObjectUrl);
    }

    if (currentSong.audioBlob) {
      this.currentObjectUrl = URL.createObjectURL(currentSong.audioBlob);
      this.audio.src = this.currentObjectUrl;
    } else if (currentSong.audioUrl || currentSong.url) {
      this.audio.src = currentSong.audioUrl || currentSong.url;
    }

    let coverUrl = null;
    if (currentSong.coverBlob) {
      try {
        coverUrl = URL.createObjectURL(currentSong.coverBlob);
      } catch(e) { coverUrl = null; }
    }

    this.setupMediaSession();
    this.updateMediaSessionMetadata(currentSong, coverUrl);

    if (this.onTrackChange) {
      this.onTrackChange(currentSong, coverUrl, this.currentIndex);
    }
  }

  async play() {
    if (this.audioContext && this.audioContext.state === 'suspended') {
      try {
        await this.audioContext.resume();
      } catch (e) {}
    }
    if (this.currentIndex === -1 && this.queue.length > 0) {
      this.currentIndex = 0;
      this.loadCurrentTrack();
    }
    if ('mediaSession' in navigator) {
      navigator.mediaSession.playbackState = 'playing';
    }
    return this.audio.play();
  }

  pause() {
    this.audio.pause();
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  next() {
    if (this.queue.length === 0) return;
    if (this.repeatMode === 'one') {
      this.audio.currentTime = 0;
      this.play();
      return;
    }
    if (this.currentIndex < this.queue.length - 1) {
      this.currentIndex++;
    } else if (this.repeatMode === 'all') {
      this.currentIndex = 0;
    } else {
      this.pause();
      return;
    }
    this.loadCurrentTrack();
    this.play();
  }

  prev() {
    if (this.queue.length === 0) return;
    if (this.audio.currentTime > 3) {
      this.audio.currentTime = 0;
      return;
    }
    if (this.currentIndex > 0) {
      this.currentIndex--;
    } else if (this.repeatMode === 'all') {
      this.currentIndex = this.queue.length - 1;
    } else {
      this.audio.currentTime = 0;
      return;
    }
    this.loadCurrentTrack();
    this.play();
  }

  handleTrackEnded() {
    if (this.repeatMode === 'one') {
      this.audio.currentTime = 0;
      this.play();
    } else {
      this.next();
    }
  }

  seek(seconds) {
    if (isFinite(seconds)) {
      this.audio.currentTime = Math.max(0, Math.min(seconds, this.audio.duration || 0));
    }
  }

  setVolume(val) {
    const safeVolume = Math.max(0, Math.min(1, parseFloat(val) || 0));
    this.audio.volume = safeVolume;
    
    if (!this.audioContext) {
      this.initAudioContext();
    }

    if (this.gainNode && this.audioContext) {
      try {
        this.gainNode.gain.setValueAtTime(safeVolume, this.audioContext.currentTime);
      } catch (e) {
        this.gainNode.gain.value = safeVolume;
      }
    }
  }

  toggleRepeatMode() {
    const modes = ['off', 'all', 'one'];
    const nextIdx = (modes.indexOf(this.repeatMode) + 1) % modes.length;
    this.repeatMode = modes[nextIdx];
    return this.repeatMode;
  }

  toggleShuffle() {
    this.isShuffle = !this.isShuffle;
    const currentSong = this.queue[this.currentIndex];
    if (this.isShuffle) {
      this.queue = this.shuffleArray([...this.originalQueue]);
    } else {
      this.queue = [...this.originalQueue];
    }
    if (currentSong) {
      this.currentIndex = this.queue.findIndex(s => s.id === currentSong.id);
    }
    if (this.onQueueChange) this.onQueueChange(this.queue);
    return this.isShuffle;
  }

  setEQBandGain(index, gainDb) {
    this.initAudioContext();
    if (this.eqFilters[index]) {
      this.eqFilters[index].gain.value = gainDb;
    }
    this.updateHeadroom();
  }

  applyEQPreset(presetName) {
    this.initAudioContext();
    const gains = this.eqPresets[presetName] || this.eqPresets.flat;
    gains.forEach((gain, idx) => this.setEQBandGain(idx, gain));
    return gains;
  }

  shuffleArray(arr) {
    const array = [...arr];
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  getCurrentSong() {
    return this.queue[this.currentIndex] || null;
  }
}

export const playerEngine = new AudioPlayerEngine();
