import cv2

cap = cv2.VideoCapture('./x.mp4')

# variabel untuk seleksi
selecting = False
initBB = None
tracker = None
x0, y0, x1, y1 = 0, 0, 0, 0

def mouse_callback(event, x, y, flags, param):
    global x0, y0, x1, y1, selecting, initBB, tracker

    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        x0, y0 = x, y

    elif event == cv2.EVENT_MOUSEMOVE and selecting:
        x1, y1 = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False
        x1, y1 = x, y
        initBB = (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, initBB)
        print("Tracking dimulai pada area:", initBB)

cv2.namedWindow("Tracking")
cv2.setMouseCallback("Tracking", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # jika sedang klik-drag, tampilkan kotak hijau
    if selecting:
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)

    # jika sudah ada tracker, update posisi objek
    if tracker is not None:
        success, box = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            cv2.putText(frame, "Tracking", (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "Lost", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()