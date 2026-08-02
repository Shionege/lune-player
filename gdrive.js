/**
 * gdrive.js - Google Drive Sync & Backup Manager for Lune Player
 * Handles OAuth2 authentication, uploading IndexedDB songs/playlists to Google Drive,
 * restoring library from Google Drive, and importing individual audio files.
 */

import { musicStorage } from './storage.js';

// Default OAuth Scope for Drive App Data & File Access
const DRIVE_SCOPES = 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email';
const FOLDER_NAME = 'LunePlayer_Backup';

class GDriveSync {
  constructor() {
    this.accessToken = localStorage.getItem('gdrive_token') || null;
    this.userEmail = localStorage.getItem('gdrive_user_email') || null;
    this.tokenClient = null;
    this.folderId = null;
  }

  /**
   * Check if user is currently connected
   */
  isConnected() {
    return !!this.accessToken;
  }

  getUserEmail() {
    return this.userEmail || 'Terhubung (Akun Google)';
  }

  /**
   * Initialize Google Auth Client
   */
  initAuth(clientId, onStatusChange) {
    if (!window.google || !window.google.accounts) {
      console.warn("Google Identity Services library not loaded yet.");
      return;
    }

    this.tokenClient = window.google.accounts.oauth2.initTokenClient({
      client_id: clientId,
      scope: DRIVE_SCOPES,
      callback: async (response) => {
        if (response.error) {
          console.error("Google Auth Error:", response);
          if (onStatusChange) onStatusChange(false, response.error);
          return;
        }

        this.accessToken = response.access_token;
        localStorage.setItem('gdrive_token', this.accessToken);

        // Fetch User Info
        try {
          const userRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
            headers: { Authorization: `Bearer ${this.accessToken}` }
          });
          if (userRes.ok) {
            const userData = await userRes.json();
            this.userEmail = userData.email;
            localStorage.setItem('gdrive_user_email', this.userEmail);
          }
        } catch (e) {
          console.warn("Failed to fetch user profile:", e);
        }

        if (onStatusChange) onStatusChange(true, null);
      }
    });
  }

  /**
   * Trigger Google Login Popup
   */
  login() {
    if (this.tokenClient) {
      this.tokenClient.requestAccessToken({ prompt: 'consent' });
    } else {
      alert("Google Client ID belum diisi atau library belum siap.");
    }
  }

  /**
   * Disconnect / Logout
   */
  logout() {
    if (this.accessToken && window.google && window.google.accounts) {
      window.google.accounts.oauth2.revoke(this.accessToken, () => {
        console.log("Token revoked");
      });
    }
    this.accessToken = null;
    this.userEmail = null;
    localStorage.removeItem('gdrive_token');
    localStorage.removeItem('gdrive_user_email');
  }

  /**
   * Get or Create Backup Folder in Google Drive
   */
  async getOrCreateBackupFolder() {
    if (this.folderId) return this.folderId;

    const query = encodeURIComponent(`name = '${FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`);
    const res = await fetch(`https://www.googleapis.com/drive/v3/files?q=${query}`, {
      headers: { Authorization: `Bearer ${this.accessToken}` }
    });

    if (!res.ok) throw new Error(`Drive folder query failed: ${res.statusText}`);
    const data = await res.json();

    if (data.files && data.files.length > 0) {
      this.folderId = data.files[0].id;
      return this.folderId;
    }

    // Create Folder
    const createRes = await fetch('https://www.googleapis.com/drive/v3/files', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: FOLDER_NAME,
        mimeType: 'application/vnd.google-apps.folder'
      })
    });

    if (!createRes.ok) throw new Error("Gagal membuat folder backup di Google Drive");
    const newFolder = await createRes.json();
    this.folderId = newFolder.id;
    return this.folderId;
  }

  /**
   * Backup all songs & playlists to Google Drive
   */
  async backupLibrary(onProgress) {
    if (!this.isConnected()) throw new Error("Belum terhubung ke Google Drive");

    const songs = await musicStorage.getAllSongs();
    const playlists = await musicStorage.getAllPlaylists();
    const folderId = await this.getOrCreateBackupFolder();

    const totalSteps = songs.length + 1; // songs + manifest
    let currentStep = 0;

    // 1. Upload metadata manifest
    const manifestData = {
      backupDate: new Date().toISOString(),
      playlists: playlists,
      songs: songs.map(s => ({
        id: s.id,
        title: s.title,
        artist: s.artist,
        album: s.album,
        duration: s.duration,
        isFavorite: s.isFavorite,
        fileName: s.fileName,
        fileType: s.fileType,
        coverArt: s.coverArt || null
      }))
    };

    if (onProgress) onProgress(currentStep, totalSteps, "Mengunggah manifest backup...");

    await this.uploadFileToDrive(
      'lune_manifest.json',
      new Blob([JSON.stringify(manifestData, null, 2)], { type: 'application/json' }),
      'application/json',
      folderId
    );

    currentStep++;

    // 2. Upload audio files
    for (const song of songs) {
      if (onProgress) onProgress(currentStep, totalSteps, `Mengunggah: ${song.title}`);

      if (song.audioData) {
        const driveFileName = `song_${song.id}.${song.fileName.split('.').pop() || 'mp3'}`;
        await this.uploadFileToDrive(
          driveFileName,
          song.audioData,
          song.fileType || 'audio/mpeg',
          folderId
        );
      }
      currentStep++;
    }

    if (onProgress) onProgress(totalSteps, totalSteps, "Backup selesai 100%!");
  }

  /**
   * Restore all songs & playlists from Google Drive
   */
  async restoreLibrary(onProgress) {
    if (!this.isConnected()) throw new Error("Belum terhubung ke Google Drive");

    const folderId = await this.getOrCreateBackupFolder();

    // Find manifest file
    const query = encodeURIComponent(`name = 'lune_manifest.json' and '${folderId}' in parents and trashed = false`);
    const res = await fetch(`https://www.googleapis.com/drive/v3/files?q=${query}`, {
      headers: { Authorization: `Bearer ${this.accessToken}` }
    });

    if (!res.ok) throw new Error("Gagal mencari file backup di Google Drive");
    const data = await res.json();

    if (!data.files || data.files.length === 0) {
      throw new Error("File backup 'lune_manifest.json' tidak ditemukan di Google Drive Anda.");
    }

    const manifestFileId = data.files[0].id;
    if (onProgress) onProgress(0, 100, "Mengunduh manifest backup...");

    // Download manifest
    const manifestRes = await fetch(`https://www.googleapis.com/drive/v3/files/${manifestFileId}?alt=media`, {
      headers: { Authorization: `Bearer ${this.accessToken}` }
    });

    if (!manifestRes.ok) throw new Error("Gagal mengunduh manifest backup");
    const manifest = await manifestRes.json();

    // List all files in backup folder
    const listQuery = encodeURIComponent(`'${folderId}' in parents and trashed = false`);
    const listRes = await fetch(`https://www.googleapis.com/drive/v3/files?q=${listQuery}`, {
      headers: { Authorization: `Bearer ${this.accessToken}` }
    });
    const driveFiles = (await listRes.json()).files || [];

    const totalSongs = manifest.songs.length;
    let loadedCount = 0;

    for (const songMeta of manifest.songs) {
      if (onProgress) onProgress(loadedCount + 1, totalSongs, `Mengunduh: ${songMeta.title}`);

      const driveFileName = `song_${songMeta.id}.${songMeta.fileName.split('.').pop() || 'mp3'}`;
      const matchingFile = driveFiles.find(f => f.name === driveFileName);

      if (matchingFile) {
        const audioRes = await fetch(`https://www.googleapis.com/drive/v3/files/${matchingFile.id}?alt=media`, {
          headers: { Authorization: `Bearer ${this.accessToken}` }
        });

        if (audioRes.ok) {
          const audioBlob = await audioRes.blob();
          const fullSongData = {
            ...songMeta,
            audioData: audioBlob,
            dateAdded: Date.now()
          };
          await musicStorage.saveSong(fullSongData);
        }
      }
      loadedCount++;
    }

    // Restore playlists
    if (manifest.playlists && Array.isArray(manifest.playlists)) {
      for (const pl of manifest.playlists) {
        await musicStorage.savePlaylist(pl);
      }
    }

    if (onProgress) onProgress(totalSongs, totalSongs, "Restorasi library dari Google Drive sukses!");
  }

  /**
   * Helper: Upload single file to Drive folder via multipart API
   */
  async uploadFileToDrive(fileName, blob, mimeType, parentFolderId) {
    // Check if file already exists in folder (replace/update)
    const checkQuery = encodeURIComponent(`name = '${fileName}' and '${parentFolderId}' in parents and trashed = false`);
    const checkRes = await fetch(`https://www.googleapis.com/drive/v3/files?q=${checkQuery}`, {
      headers: { Authorization: `Bearer ${this.accessToken}` }
    });
    const checkData = await checkRes.json();
    let existingFileId = null;
    if (checkData.files && checkData.files.length > 0) {
      existingFileId = checkData.files[0].id;
    }

    const metadata = {
      name: fileName,
      mimeType: mimeType
    };
    if (!existingFileId) {
      metadata.parents = [parentFolderId];
    }

    const form = new FormData();
    form.append('metadata', new Blob([JSON.stringify(metadata)], { type: 'application/json' }));
    form.append('file', blob);

    const uploadUrl = existingFileId
      ? `https://www.googleapis.com/upload/drive/v3/files/${existingFileId}?uploadType=multipart`
      : `https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart`;

    const res = await fetch(uploadUrl, {
      method: existingFileId ? 'PATCH' : 'POST',
      headers: { Authorization: `Bearer ${this.accessToken}` },
      body: form
    });

    if (!res.ok) {
      throw new Error(`Upload ${fileName} gagal (${res.status})`);
    }

    return await res.json();
  }
}

export const gdriveSync = new GDriveSync();
