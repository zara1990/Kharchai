/**
 * Lightweight, on-device image quality checks for receipt capture.
 *
 * No backend, no OpenAI, no extra dependencies.
 *
 * ── Blur detection ────────────────────────────────────────────────────────────
 * A blurry JPEG contains far fewer high-frequency edge details.  JPEG's DCT
 * encoding spends bits on those edges, so a blurry image compresses much more
 * aggressively at a fixed quality setting (0.85) than a sharp one.  By dividing
 * the approximate byte size (base64.length × 0.75) by the image's megapixel
 * count we get a resolution-independent metric.  Below BLUR_BYTES_PER_MP the
 * image is flagged as blurry.
 *
 * Typical values (quality 0.85):
 *   sharp receipt   → 150,000 – 400,000 bytes/MP
 *   mildly blurry   →  80,000 – 150,000 bytes/MP
 *   very blurry     →          < 80,000 bytes/MP
 *
 * Threshold set at 65,000 bytes/MP — conservative to avoid false positives on
 * plain-white receipts which have fewer edges by nature.
 *
 * ── Lighting detection ────────────────────────────────────────────────────────
 * EXIF BrightnessValue is an EV (exposure value) number the camera records as
 * the average scene luminance.  Negative or near-zero values indicate a dark
 * scene.  Most modern Android cameras populate this field.  If it is absent the
 * check is skipped (no false positives on devices that omit the tag).
 *
 * Typical values:
 *   well-lit indoor  →  2 – 5 EV
 *   dim indoor       →  0 – 2 EV
 *   too dark         →    < 0.5 EV
 */

export type QualityIssue = 'blur' | 'dark';

/** Bytes-per-megapixel below this value → blur warning */
const BLUR_BYTES_PER_MP_THRESHOLD = 65_000;

/** EXIF BrightnessValue (EV) below this value → dark warning */
const DARK_BRIGHTNESS_EV_THRESHOLD = 0.5;

export interface QualityInput {
  /** Raw base64-encoded JPEG string (with or without data-URI prefix). */
  base64: string;
  /** Image width in pixels, as returned by takePictureAsync. */
  width: number;
  /** Image height in pixels, as returned by takePictureAsync. */
  height: number;
  /** EXIF object from takePictureAsync({ exif: true }), may be undefined. */
  exif?: Record<string, unknown>;
}

/**
 * Returns an array of detected QualityIssue values.
 * An empty array means the image passed all checks.
 * This function is synchronous and O(1) — safe to call immediately after capture.
 */
export function checkImageQuality(input: QualityInput): QualityIssue[] {
  const issues: QualityIssue[] = [];

  // ── Blur check ─────────────────────────────────────────────────────────────
  // Strip the optional data-URI prefix before measuring length.
  const raw = input.base64.includes(',')
    ? input.base64.split(',')[1]
    : input.base64;

  // base64 encodes every 3 source bytes as 4 characters → multiply by 0.75
  const approxBytes = raw.length * 0.75;
  const megapixels = (input.width * input.height) / 1_000_000;

  if (megapixels > 0.1) {
    // Only apply the check if we have at least 0.1 MP (sanity guard)
    const bytesPerMP = approxBytes / megapixels;
    if (bytesPerMP < BLUR_BYTES_PER_MP_THRESHOLD) {
      issues.push('blur');
    }
  }

  // ── Lighting check ─────────────────────────────────────────────────────────
  if (input.exif) {
    const bv = input.exif['BrightnessValue'];
    if (typeof bv === 'number' && bv < DARK_BRIGHTNESS_EV_THRESHOLD) {
      issues.push('dark');
    }
  }

  return issues;
}

/** Human-readable warning message for the detected issues. */
export function qualityWarningMessage(issues: QualityIssue[]): string {
  const hasBlur = issues.includes('blur');
  const hasDark = issues.includes('dark');

  if (hasBlur && hasDark) {
    return (
      'This photo looks blurry and the lighting is poor.\n' +
      'For the best results, retake in a well-lit area and hold the camera steady.'
    );
  }
  if (hasBlur) {
    return 'This photo looks blurry. Please retake it for better results.';
  }
  if (hasDark) {
    return 'The receipt is difficult to read. Try taking the photo in better lighting.';
  }
  return '';
}
