import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ImageQualityResult:
    """Holds the outcome of a single image quality check."""
    passed: bool
    score: Optional[float] = None   # 0.0–1.0 where applicable
    detail: Optional[str] = None


@dataclass
class ImageQualityReport:
    """Aggregated result of all quality checks for one image."""
    blur: ImageQualityResult = field(default_factory=lambda: ImageQualityResult(passed=False))
    brightness: ImageQualityResult = field(default_factory=lambda: ImageQualityResult(passed=False))
    glare: ImageQualityResult = field(default_factory=lambda: ImageQualityResult(passed=False))
    resolution: ImageQualityResult = field(default_factory=lambda: ImageQualityResult(passed=False))
    receipt_present: ImageQualityResult = field(default_factory=lambda: ImageQualityResult(passed=False))
    long_receipt: ImageQualityResult = field(default_factory=lambda: ImageQualityResult(passed=False))

    @property
    def overall_passed(self) -> bool:
        """True only when every check passes."""
        return all([
            self.blur.passed,
            self.brightness.passed,
            self.glare.passed,
            self.resolution.passed,
            self.receipt_present.passed,
        ])


class ImageQualityService:
    """
    Analyses receipt image quality before AI extraction.

    Each method is a standalone check so they can be added incrementally.
    All methods currently return placeholder results.

    TODO (future milestone): replace each stub with a real OpenCV / PIL
    implementation once the image processing layer is introduced.
    """

    async def detect_blur(self, image_bytes: bytes) -> ImageQualityResult:
        """
        Detect whether the image is too blurry for reliable text extraction.

        TODO: Implement using Laplacian variance (OpenCV).
              A variance below ~100 typically indicates blur.

        Args:
            image_bytes: Raw image bytes (JPEG / PNG).

        Returns:
            ImageQualityResult with passed=True when sharpness is sufficient.
        """
        # TODO: implement blur detection
        logger.debug("detect_blur called — returning placeholder result")
        return ImageQualityResult(passed=True, detail="Blur check not yet implemented")

    async def detect_brightness(self, image_bytes: bytes) -> ImageQualityResult:
        """
        Check whether the image is too dark or overexposed.

        TODO: Implement by converting to HSV and examining the V channel mean.
              Acceptable range: roughly 50–220 on a 0–255 scale.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            ImageQualityResult with passed=True when brightness is acceptable.
        """
        # TODO: implement brightness detection
        logger.debug("detect_brightness called — returning placeholder result")
        return ImageQualityResult(passed=True, detail="Brightness check not yet implemented")

    async def detect_glare(self, image_bytes: bytes) -> ImageQualityResult:
        """
        Detect bright reflective glare that obscures receipt text.

        TODO: Implement by thresholding very bright pixels (>240) and
              computing the proportion of the image they occupy.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            ImageQualityResult with passed=True when glare is below threshold.
        """
        # TODO: implement glare detection
        logger.debug("detect_glare called — returning placeholder result")
        return ImageQualityResult(passed=True, detail="Glare check not yet implemented")

    async def detect_resolution(self, image_bytes: bytes) -> ImageQualityResult:
        """
        Verify that the image has enough pixels for reliable OCR / Vision.

        TODO: Implement by decoding image dimensions and checking that both
              width and height meet a minimum threshold (e.g. 400 × 600 px).

        Args:
            image_bytes: Raw image bytes.

        Returns:
            ImageQualityResult with passed=True when resolution is sufficient.
        """
        # TODO: implement resolution check
        logger.debug("detect_resolution called — returning placeholder result")
        return ImageQualityResult(passed=True, detail="Resolution check not yet implemented")

    async def detect_receipt_presence(self, image_bytes: bytes) -> ImageQualityResult:
        """
        Determine whether a receipt is actually present in the image.

        TODO: Implement using a lightweight classifier or heuristic (e.g.
              checking for long vertical white regions typical of receipts,
              or a small ML model fine-tuned for receipt detection).

        Args:
            image_bytes: Raw image bytes.

        Returns:
            ImageQualityResult with passed=True when a receipt is detected.
        """
        # TODO: implement receipt presence detection
        logger.debug("detect_receipt_presence called — returning placeholder result")
        return ImageQualityResult(passed=True, detail="Receipt presence check not yet implemented")

    async def detect_long_receipt(self, image_bytes: bytes) -> ImageQualityResult:
        """
        Flag receipts that are unusually long and may need to be split or
        processed in sections.

        TODO: Implement by checking the image aspect ratio. An extreme
              height-to-width ratio (e.g. > 5:1) suggests a long receipt.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            ImageQualityResult with passed=True when the receipt fits in a
            single pass, or False when multi-section processing is advised.
        """
        # TODO: implement long-receipt detection
        logger.debug("detect_long_receipt called — returning placeholder result")
        return ImageQualityResult(passed=True, detail="Long-receipt check not yet implemented")

    async def run_all(self, image_bytes: bytes) -> ImageQualityReport:
        """
        Run every quality check and return a consolidated report.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            ImageQualityReport summarising all check outcomes.
        """
        return ImageQualityReport(
            blur=await self.detect_blur(image_bytes),
            brightness=await self.detect_brightness(image_bytes),
            glare=await self.detect_glare(image_bytes),
            resolution=await self.detect_resolution(image_bytes),
            receipt_present=await self.detect_receipt_presence(image_bytes),
            long_receipt=await self.detect_long_receipt(image_bytes),
        )
