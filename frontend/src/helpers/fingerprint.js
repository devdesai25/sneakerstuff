import FingerprintJS from '@fingerprintjs/fingerprintjs';

let fpPromise = null;

export const getVisitorId = async () => {
  try {
    if (!fpPromise) {
      fpPromise = FingerprintJS.load();
    }
    const fp = await fpPromise;
    const result = await fp.get();
    return result.visitorId;
  } catch (error) {
    console.error('Failed to generate device fingerprint:', error);
    return null;
  }
};
