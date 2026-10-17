"""Offline person detection helpers for user-selected media."""
import cv2


def detect_people(image, confidence=0.5):
    """Return (x, y, width, height, confidence) HOG person detections."""
    if image is None or image.size == 0:
        return []
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    rects, weights = hog.detectMultiScale(image, winStride=(8, 8), padding=(8, 8), scale=1.05)
    threshold = float(confidence) * 2.0 - 1.0
    return [(int(x), int(y), int(w), int(h), float(score))
            for (x, y, w, h), score in zip(rects, weights.flatten()) if float(score) >= threshold]


def draw_detections(image, detections, color=(0, 255, 210), opacity=0.85):
    result = image.copy()
    layer = result.copy()
    for x, y, w, h, score in detections:
        cv2.rectangle(layer, (x, y), (x + w, y + h), color, 2)
        cv2.putText(layer, f"PERSON {score:.2f}", (x, max(18, y - 7)),
                    cv2.FONT_HERSHEY_SIMPLEX, .55, color, 2, cv2.LINE_AA)
    alpha = min(1.0, max(0.0, float(opacity)))
    cv2.addWeighted(layer, alpha, result, 1.0 - alpha, 0, result)
    return result
