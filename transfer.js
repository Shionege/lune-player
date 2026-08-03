/**
 * transfer.js - Wi-Fi P2P Music Transfer Engine using WebRTC (PeerJS)
 * Generates 6-digit PIN code for receiver mode & handles binary ArrayBuffer chunk transfer.
 */

class PeerTransferEngine {
  constructor() {
    this.peer = null;
    this.connection = null;
    this.currentPin = null;

    this.onPinGenerated = null;
    this.onPeerConnected = null;
    this.onPeerDisconnected = null;
    this.onTransferProgress = null;
    this.onFileReceived = null;
    this.onError = null;

    this.incomingFile = null;
  }

  generate6DigitPin() {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  /**
   * Start Receiver Mode (generates PIN code)
   */
  startReceiverMode() {
    if (this.peer) this.peer.destroy();

    const pin = this.generate6DigitPin();
    this.currentPin = pin;
    const peerId = `anywhere-pwa-${pin}`;

    if (!window.Peer) {
      if (this.onError) this.onError("PeerJS library not loaded. Ensure internet or cache is available.");
      return pin;
    }

    try {
      this.peer = new window.Peer(peerId, {
        debug: 1,
      });

      this.peer.on('open', (id) => {
        console.log('Peer Receiver registered with ID:', id);
        if (this.onPinGenerated) this.onPinGenerated(this.currentPin);
      });

      this.peer.on('connection', (conn) => {
        console.log('Incoming connection from sender');
        this.connection = conn;
        this.setupConnectionHandlers(conn);
        if (this.onPeerConnected) this.onPeerConnected(conn.peer);
      });

      this.peer.on('error', (err) => {
        console.error('Peer Receiver error:', err);
        // If ID taken, retry with new PIN
        if (err.type === 'unavailable-id') {
          this.startReceiverMode();
        } else if (this.onError) {
          this.onError(err.message || 'Peer connection error');
        }
      });
    } catch (e) {
      console.error('Failed to init Peer:', e);
    }

    return pin;
  }

  /**
   * Start Sender Mode (connect to receiver using PIN)
   */
  connectToReceiver(pin) {
    if (!window.Peer) {
      if (this.onError) this.onError("PeerJS library not loaded.");
      return;
    }

    if (this.peer) this.peer.destroy();

    const senderId = `anywhere-sender-${Date.now()}`;
    this.peer = new window.Peer(senderId, { debug: 1 });

    this.peer.on('open', () => {
      const targetPeerId = `anywhere-pwa-${pin}`;
      console.log('Connecting to receiver target:', targetPeerId);
      const conn = this.peer.connect(targetPeerId, { reliable: true });
      this.connection = conn;
      this.setupConnectionHandlers(conn);
    });

    this.peer.on('error', (err) => {
      console.error('Peer Sender error:', err);
      if (this.onError) this.onError(`Could not connect to PIN ${pin}. Verify PIN & network.`);
    });
  }

  setupConnectionHandlers(conn) {
    conn.on('open', () => {
      console.log('P2P DataChannel open and ready!');
      if (this.onPeerConnected) this.onPeerConnected(conn.peer);
    });

    conn.on('data', (data) => {
      this.handleIncomingData(data);
    });

    conn.on('close', () => {
      console.log('P2P Connection closed');
      if (this.onPeerDisconnected) this.onPeerDisconnected();
    });

    conn.on('error', (err) => {
      console.error('DataChannel error:', err);
      if (this.onError) this.onError('Data transfer error');
    });
  }

  handleIncomingData(data) {
    if (typeof data === 'object' && data && data.type === 'start') {
      this.incomingFile = {
        meta: data.meta,
        chunks: [],
        receivedSize: 0,
      };
      if (this.onTransferProgress) {
        this.onTransferProgress(0, data.meta.name);
      }
    } else if (data instanceof ArrayBuffer || data instanceof Uint8Array || data instanceof Blob || (typeof data === 'object' && data && data.chunk)) {
      if (this.incomingFile) {
        const rawChunk = (data && data.chunk) ? data.chunk : data;
        this.incomingFile.chunks.push(rawChunk);
        const chunkSize = rawChunk.byteLength || rawChunk.size || 0;
        this.incomingFile.receivedSize += chunkSize;
        const totalSize = this.incomingFile.meta ? this.incomingFile.meta.size : 1;
        const progress = Math.min(100, Math.round((this.incomingFile.receivedSize / totalSize) * 100));
        if (this.onTransferProgress) {
          this.onTransferProgress(progress, this.incomingFile.meta ? this.incomingFile.meta.name : 'audio');
        }
      }
    } else if (typeof data === 'object' && data && data.type === 'end') {
      if (this.incomingFile && this.incomingFile.chunks.length > 0) {
        const metaType = (this.incomingFile.meta && this.incomingFile.meta.type) ? this.incomingFile.meta.type : 'audio/mpeg';
        const metaName = (this.incomingFile.meta && this.incomingFile.meta.name) ? this.incomingFile.meta.name : `received_song_${Date.now()}.mp3`;
        
        const fullBlob = new Blob(this.incomingFile.chunks, { type: metaType });
        const fileObj = new File([fullBlob], metaName, { type: fullBlob.type || 'audio/mpeg' });
        
        if (this.onFileReceived) {
          this.onFileReceived(fileObj);
        }
        this.incomingFile = null;
      }
    }
  }

  /**
   * Send file to connected Peer in ArrayBuffer chunks with WebRTC Backpressure Throttling
   */
  async sendFile(file) {
    if (!this.connection || !this.connection.open) {
      if (this.onError) this.onError("No active Peer connection. Enter PIN first.");
      return;
    }

    const chunkSize = 32 * 1024; // 32KB chunks for WebRTC stability
    const totalSize = file.size;

    // Send start metadata
    this.connection.send({
      type: 'start',
      meta: {
        name: file.name,
        size: totalSize,
        type: file.type || 'audio/mpeg',
      },
    });

    const arrayBuffer = await file.arrayBuffer();
    let offset = 0;
    const dc = this.connection.dataChannel || this.connection._dc;

    while (offset < totalSize) {
      // WebRTC Backpressure Check: wait if buffer exceeds 128KB
      while (dc && dc.bufferedAmount > 128 * 1024) {
        await new Promise((r) => setTimeout(r, 20));
      }

      const chunk = arrayBuffer.slice(offset, offset + chunkSize);
      this.connection.send(chunk);
      offset += chunkSize;

      const progress = Math.min(100, Math.round((offset / totalSize) * 100));
      if (this.onTransferProgress) {
        this.onTransferProgress(progress, file.name);
      }

      // Small tick delay to yield event loop
      await new Promise((r) => setTimeout(r, 10));
    }

    // Send end signal
    this.connection.send({ type: 'end' });
  }

  destroy() {
    if (this.connection) this.connection.close();
    if (this.peer) this.peer.destroy();
  }
}

export const peerTransfer = new PeerTransferEngine();
