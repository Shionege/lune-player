/**
 * storage.js - IndexedDB Wrapper for Anywhere Music Player
 * Handles offline storage of Audio Blobs, ID3 Metadata, Cover Art, and Playlists.
 */

const DB_NAME = 'AnywhereMusicDB';
const DB_VERSION = 1;

class MusicStorage {
  constructor() {
    this.db = null;
    this.initPromise = this.initDB();
  }

  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Songs Store
        if (!db.objectStoreNames.contains('songs')) {
          const songStore = db.createObjectStore('songs', { keyPath: 'id' });
          songStore.createIndex('title', 'title', { unique: false });
          songStore.createIndex('artist', 'artist', { unique: false });
          songStore.createIndex('album', 'album', { unique: false });
          songStore.createIndex('isFavorite', 'isFavorite', { unique: false });
          songStore.createIndex('dateAdded', 'dateAdded', { unique: false });
        }

        // Playlists Store
        if (!db.objectStoreNames.contains('playlists')) {
          const playlistStore = db.createObjectStore('playlists', { keyPath: 'id' });
          playlistStore.createIndex('name', 'name', { unique: false });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        this.requestPersistentStorage().catch(() => {});
        resolve(this.db);
      };

      request.onerror = (event) => {
        console.error('IndexedDB Error:', event.target.error);
        reject(event.target.error);
      };
    });
  }

  async ensureDB() {
    if (!this.db) {
      await this.initPromise;
    }
  }

  /**
   * Save or update a song record
   * @param {Object} song { id, title, artist, album, audioBlob, coverBlob, duration, explicit, isFavorite, dateAdded }
   */
  async saveSong(song) {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('songs', 'readwrite');
      const store = tx.objectStore('songs');
      const request = store.put(song);

      request.onsuccess = () => resolve(song);
      request.onerror = (e) => reject(e.target.error);
    });
  }

  /**
   * Bulk save array of songs
   */
  async saveSongsBatch(songs) {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('songs', 'readwrite');
      const store = tx.objectStore('songs');
      songs.forEach((song) => store.put(song));

      tx.oncomplete = () => resolve(true);
      tx.onerror = (e) => reject(e.target.error);
    });
  }

  /**
   * Get all songs sorted by dateAdded descending
   */
  async getAllSongs() {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('songs', 'readonly');
      const store = tx.objectStore('songs');
      const request = store.getAll();

      request.onsuccess = () => {
        const songs = request.result || [];
        songs.sort((a, b) => (b.dateAdded || 0) - (a.dateAdded || 0));
        resolve(songs);
      };
      request.onerror = (e) => reject(e.target.error);
    });
  }

  /**
   * Toggle favorite status of a song (100% fail-safe lookup)
   */
  async toggleFavorite(id) {
    await this.ensureDB();
    const songs = await this.getAllSongs();
    const targetSong = songs.find(s => String(s.id) === String(id));
    if (!targetSong) throw new Error('Song not found');

    targetSong.isFavorite = !targetSong.isFavorite;

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('songs', 'readwrite');
      const store = tx.objectStore('songs');
      const putReq = store.put(targetSong);
      putReq.onsuccess = () => resolve(targetSong.isFavorite);
      putReq.onerror = (e) => reject(e.target.error);
    });
  }

  /**
   * Delete a song by ID
   */
  async deleteSong(id) {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('songs', 'readwrite');
      const store = tx.objectStore('songs');
      const request = store.delete(id);

      request.onsuccess = () => resolve(true);
      request.onerror = (e) => reject(e.target.error);
    });
  }

  /**
   * Get all playlists
   */
  async getAllPlaylists() {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('playlists', 'readonly');
      const store = tx.objectStore('playlists');
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result || []);
      request.onerror = (e) => reject(e.target.error);
    });
  }

  /**
   * Save or update playlist
   */
  async savePlaylist(playlist) {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('playlists', 'readwrite');
      const store = tx.objectStore('playlists');
      const request = store.put(playlist);

      request.onsuccess = () => resolve(playlist);
      request.onerror = (e) => reject(e.target.error);
    });
  }

  async deletePlaylist(id) {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('playlists', 'readwrite');
      const store = tx.objectStore('playlists');
      const request = store.delete(id);

      request.onsuccess = () => resolve(true);
      request.onerror = (e) => reject(e.target.error);
    });
  }

  async exportData() {
    await this.ensureDB();
    const songs = await this.getAllSongs();
    const playlists = await this.getAllPlaylists();

    const serializedSongs = await Promise.all(songs.map(async (song) => {
      let audioBase64 = null;
      if (song.blob) {
        audioBase64 = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result);
          reader.readAsDataURL(song.blob);
        });
      }
      return {
        ...song,
        blob: undefined,
        audioDataUrl: audioBase64
      };
    }));

    return JSON.stringify({
      version: 1,
      timestamp: Date.now(),
      songs: serializedSongs,
      playlists: playlists
    }, null, 2);
  }

  async importData(jsonString) {
    await this.ensureDB();
    const data = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
    if (!data || !Array.isArray(data.songs)) {
      throw new Error("Invalid backup format.");
    }

    for (const song of data.songs) {
      let blob = null;
      if (song.audioDataUrl) {
        const res = await fetch(song.audioDataUrl);
        blob = await res.blob();
      }
      const { audioDataUrl, ...rest } = song;
      await this.saveSong({
        ...rest,
        blob: blob || rest.blob
      });
    }

    if (Array.isArray(data.playlists)) {
      for (const pl of data.playlists) {
        await this.savePlaylist(pl);
      }
    }
    return true;
  }

  async requestPersistentStorage() {
    if (navigator.storage && navigator.storage.persist) {
      try {
        const isPersisted = await navigator.storage.persisted();
        if (!isPersisted) {
          const granted = await navigator.storage.persist();
          console.log(`[Storage] Persistent storage granted: ${granted}`);
        } else {
          console.log(`[Storage] Storage is already persistent.`);
        }
      } catch (err) {
        console.warn("[Storage] Storage persistence check failed:", err);
      }
    }
  }
}

export const musicStorage = new MusicStorage();
