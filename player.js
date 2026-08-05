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
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState === 'visible') {
        // App came back to foreground — resume AudioContext if suspended
        if (this.audioContext && this.audioContext.state === 'suspended') {
          try {
            await this.audioContext.resume();
          } catch (e) {
            console.warn('AudioContext resume failed:', e);
          }
        }
        // If we were playing before backgrounding, ensure audio is still playing
        if (this.isPlaying && this.audio.paused) {
          try {
            await this.audio.play();
          } catch (e) {
            console.warn('Audio resume on foreground failed:', e);
          }
        }
      }
    });
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

      // Connect the last EQ node to the GainNode, and the GainNode to the destination
      lastNode.connect(this.gainNode);
      this.gainNode.connect(this.audioContext.destination);
    } catch (e) {
      console.warn("Web Audio API equalizer initialization failed:", e);
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

    try {
      navigator.mediaSession.setActionHandler('play', () => this.play());
      navigator.mediaSession.setActionHandler('pause', () => this.pause());
      navigator.mediaSession.setActionHandler('previoustrack', () => this.prev());
      navigator.mediaSession.setActionHandler('nexttrack', () => this.next());
      navigator.mediaSession.setActionHandler('seekto', (details) => {
        if (details.seekTime != null) {
          this.seek(details.seekTime);
        }
      });
      // Explicitly set seekforward and seekbackward to null so iOS Control Center displays Next Track & Previous Track buttons
      navigator.mediaSession.setActionHandler('seekforward', null);
      navigator.mediaSession.setActionHandler('seekbackward', null);
    } catch (e) {
      console.warn("MediaSession handler error:", e);
    }
  }

  updateMediaSessionMetadata(song, coverUrl) {
    if (!('mediaSession' in navigator) || !song) return;

    navigator.mediaSession.metadata = new MediaMetadata({
      title: song.title || 'Unknown Title',
      artist: song.artist || 'Unknown Artist',
      album: song.album || 'Lune Player',
      artwork: coverUrl ? [
        { src: coverUrl, sizes: '512x512', type: 'image/png' }
      ] : [
        { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' }
      ]
    });
  }

  updateMediaSessionState() {
    if ('mediaSession' in navigator) {
      navigator.mediaSession.playbackState = this.isPlaying ? 'playing' : 'paused';
      // Update position state for iOS lock screen scrubber
      if (this.audio.duration && isFinite(this.audio.duration)) {
        try {
          navigator.mediaSession.setPositionState({
            duration: this.audio.duration,
            playbackRate: this.audio.playbackRate,
            position: this.audio.currentTime,
          });
        } catch (e) { /* setPositionState not supported on all browsers */ }
      }
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
    } else if (currentSong.url) {
      this.audio.src = currentSong.url;
    }

    let coverUrl = null;
    if (currentSong.coverBlob) {
      try {
        coverUrl = URL.createObjectURL(currentSong.coverBlob);
      } catch(e) { coverUrl = null; }
    }

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
    const safeVolume = Math.max(0, Math.min(1, val));
    this.audio.volume = safeVolume;
    if (this.gainNode) {
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
