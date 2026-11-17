"""Downscaled plate with a labeled grid in source-pixel coordinates (for writing hints)."""
import sys
import cv2

src, out = sys.argv[1], sys.argv[2]
crop = [int(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
img = cv2.imread(src)
x0 = y0 = 0
if crop:
    x0, y0, x1, y1 = crop
    img = img[y0:y1, x0:x1]
s = 1400 / max(img.shape[:2])
small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
step = 250 if crop else 500
for v in range(0, img.shape[1], step):
    X = int(v * s); cv2.line(small, (X, 0), (X, small.shape[0]), (0, 0, 255), 1)
    cv2.putText(small, str(v + x0), (X + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
for v in range(0, img.shape[0], step):
    Y = int(v * s); cv2.line(small, (0, Y), (small.shape[1], Y), (255, 0, 0), 1)
    cv2.putText(small, str(v + y0), (2, Y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
cv2.imwrite(out, small)
