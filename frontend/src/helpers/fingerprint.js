import FingerprintJS from '@fingerprintjs/fingerprintjs';

let fpPromise = null;

// Get or create a persistent device token stored in localStorage & cookies
const getPersistentDeviceToken = () => {
  try {
    const storageKey = '__sneakerstuff_did';
    let token = localStorage.getItem(storageKey);
    if (!token) {
      // Check cookies
      const match = document.cookie.match(new RegExp('(^| )' + storageKey + '=([^;]+)'));
      if (match) {
        token = match[2];
      }
    }
    if (!token) {
      token = 'd_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
    }
    localStorage.setItem(storageKey, token);
    document.cookie = `${storageKey}=${token}; path=/; max-age=31536000; SameSite=Lax`;
    return token;
  } catch (e) {
    return 'fallback_token';
  }
};

// Extract WebGL unmasked GPU vendor and renderer
const getWebGLFingerprint = () => {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return 'no-webgl';
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (!debugInfo) return 'no-debug-info';
    const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) || '';
    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || '';
    return `${vendor}~${renderer}`;
  } catch (e) {
    return 'webgl-error';
  }
};

// SHA-256 hash helper with fallback
const hashString = async (str) => {
  try {
    if (window.crypto && window.crypto.subtle) {
      const encoder = new TextEncoder();
      const data = encoder.encode(str);
      const hashBuffer = await crypto.subtle.digest('SHA-256', data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
    }
  } catch (e) {
    // Fallback to simple hash below
  }
  let hash = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return 'fp_' + (hash >>> 0).toString(16).padStart(8, '0');
};

export const getVisitorId = async () => {
  try {
    if (!fpPromise) {
      fpPromise = FingerprintJS.load();
    }
    const fp = await fpPromise;
    const result = await fp.get();
    const fpId = result.visitorId || 'fp_unknown';

    const persistentToken = getPersistentDeviceToken();
    const gpu = getWebGLFingerprint();
    const screenSpec = `${window.screen.width}x${window.screen.height}x${window.screen.colorDepth}x${window.devicePixelRatio}`;
    const cores = navigator.hardwareConcurrency || 'unknown';
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'unknown';
    const language = navigator.language || 'unknown';
    const platform = navigator.platform || 'unknown';

    // Combine stable hardware properties + persistent token + FingerprintJS ID
    const rawFingerprint = [
      persistentToken,
      gpu,
      screenSpec,
      cores,
      timezone,
      language,
      platform,
      fpId
    ].join('||');

    const finalHash = await hashString(rawFingerprint);
    console.log('[Device Fingerprint] Generated stable device ID:', finalHash);
    return finalHash;
  } catch (error) {
    console.error('Failed to generate device fingerprint:', error);
    const persistentToken = getPersistentDeviceToken();
    const gpu = getWebGLFingerprint();
    return await hashString(`${persistentToken}||${gpu}`);
  }
};

