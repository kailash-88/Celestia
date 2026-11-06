"""OCR helpers with optimized image preprocessing and explicit confidence reporting."""

import os
from statistics import mean


def _prepare_for_ocr(source_image):
    """Downscale large images and create OpenCV variants for fast, robust OCR."""
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageOps

        # Transpose based on EXIF tag (critical for mobile camera uploads)
        oriented = ImageOps.exif_transpose(source_image)

        # Scale down large camera photos to max 1600px dimension for rapid OCR
        width, height = oriented.size
        if max(width, height) > 1600:
            oriented.thumbnail((1600, 1600), Image.Resampling.LANCZOS)

        rgb = np.asarray(oriented.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # Auto-crop bright white borders if image is a small medicine strip
        foreground = cv2.threshold(gray, 238, 255, cv2.THRESH_BINARY_INV)[1]
        points = cv2.findNonZero(foreground)
        if points is not None:
            x, y, w, h = cv2.boundingRect(points)
            image_area = gray.shape[0] * gray.shape[1]
            crop_area = w * h
            if crop_area and crop_area < image_area * 0.92 and crop_area > image_area * 0.15:
                pad = max(8, int(min(w, h) * 0.035))
                x0, y0 = max(0, x - pad), max(0, y - pad)
                x1 = min(gray.shape[1], x + w + pad)
                y1 = min(gray.shape[0], y + h + pad)
                gray = gray[y0:y1, x0:x1]

        # Enhance contrast with CLAHE
        enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        # Otsu binarization
        otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        return [Image.fromarray(enhanced), Image.fromarray(otsu)]
    except ImportError:
        from PIL import ImageEnhance, ImageOps
        oriented = ImageOps.exif_transpose(source_image)
        if max(oriented.size) > 1600:
            oriented.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        gray = ImageOps.autocontrast(oriented.convert("L"))
        return [ImageEnhance.Contrast(gray).enhance(1.4)]


def extract_prescription_data(image_path, tesseract_cmd):
    """Extract text when OCR is available; returns raw text and detected label fields."""
    result = {
        "raw_text": "",
        "fields": {
            "name": "",
            "generic_name": "",
            "dosage": "",
            "form": "",
            "purpose": "",
            "expiry_date": "",
            "ocr_confidence": None,
        },
    }
    try:
        import pytesseract
        from PIL import Image, ImageOps
    except ImportError:
        result["fields"]["unavailable"] = (
            "OCR is unavailable because Tesseract support is not installed."
        )
        return result

    if tesseract_cmd and os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        with Image.open(image_path) as source_image:
            candidates = _prepare_for_ocr(source_image)
            best_text = ""
            best_confidence = None
            best_rank = (-1, -1)

            for image in candidates:
                for psm in ("6", "3"):
                    config = f"--oem 3 --psm {psm}"
                    try:
                        data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                        words = [w.strip() for w in data.get("text", []) if w and w.strip()]
                        scores = [
                            float(s) for w, s in zip(data.get("text", []), data.get("conf", []))
                            if w and w.strip() and str(s).strip() not in ("", "-1") and float(s) >= 0
                        ]
                        conf = round(mean(scores)) if scores else None
                        char_count = sum(len(w) for w in words)
                        rank = (len(words), char_count)

                        if rank > best_rank and words:
                            best_rank = rank
                            best_confidence = conf
                            best_text = " ".join([w for w in data.get("text", []) if w]).strip()
                            # Build structured multi-line text
                            lines = []
                            cur_line = []
                            last_line_num = None
                            for word, line_num in zip(data.get("text", []), data.get("line_num", [])):
                                if line_num != last_line_num:
                                    if cur_line:
                                        lines.append(" ".join(cur_line))
                                        cur_line = []
                                    last_line_num = line_num
                                if word and word.strip():
                                    cur_line.append(word.strip())
                            if cur_line:
                                lines.append(" ".join(cur_line))
                            if lines:
                                best_text = "\n".join(lines)
                    except Exception:
                        continue

            # Fallback to direct image_to_string if image_to_data returned sparse tokens
            if not best_text and candidates:
                best_text = pytesseract.image_to_string(candidates[0], config="--oem 3 --psm 6").strip()

            result["raw_text"] = best_text.strip()
            result["fields"]["ocr_confidence"] = best_confidence

    except pytesseract.pytesseract.TesseractNotFoundError:
        result["fields"]["unavailable"] = (
            "Tesseract OCR is not installed or its path is incorrect. Install Tesseract and set TESSERACT_CMD in .env."
        )
        return result
    except Exception as error:
        result["fields"]["unavailable"] = f"OCR could not process this image ({type(error).__name__})."
        return result

    lines = [line.strip() for line in result["raw_text"].splitlines() if line.strip()]
    if lines:
        cand = next((l for l in lines if len(l) > 2 and not any(h in l.lower() for h in ["hospital", "prescription", "doctor", "patient", "clinic", "phone"])), lines[0])
        result["fields"]["name"] = cand
    if not result["raw_text"]:
        result["fields"]["unavailable"] = (
            "No readable text was found. Enter details manually after checking the image."
        )
    return result
