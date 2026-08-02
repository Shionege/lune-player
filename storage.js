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
   * Toggle favorite status of a song (supports both string & numeric ID lookups)
   */
  async toggleFavorite(id) {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('songs', 'readwrite');
      const store = tx.objectStore('songs');
      
      const getReq = store.get(id);

      getReq.onsuccess = () => {
        let song = getReq.result;

        const performToggle = (targetSong) => {
          targetSong.isFavorite = !targetSong.isFavorite;
          const putReq = store.put(targetSong);
          putReq.onsuccess = () => resolve(targetSong.isFavorite);
          putReq.onerror = (e) => reject(e.target.error);
        };

        if (song) {
          performToggle(song);
          return;
        }

        // Fallback: try numeric ID if string lookup returned undefined
        if (!isNaN(Number(id))) {
          const numReq = store.get(Number(id));
          numReq.onsuccess = () => {
            const numSong = numReq.result;
            if (!numSong) {
              reject(new Error('Song not found'));
              return;
            }
            performToggle(numSong);
          };
          numReq.onerror = (e) => reject(e.target.error);
        } else {
          reject(new Error('Song not found'));
        }
      };
      getReq.onerror = (e) => reject(e.target.error);
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

  async clearAllData() {
    await this.ensureDB();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(['songs', 'playlists'], 'readwrite');
      tx.objectStore('songs').clear();
      tx.objectStore('playlists').clear();
      tx.oncomplete = () => resolve(true);
      tx.onerror = (e) => reject(e.target.error);
    });
  }
}

export const musicStorage = new MusicStorage();
