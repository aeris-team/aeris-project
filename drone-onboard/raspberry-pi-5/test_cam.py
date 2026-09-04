import cv2

print("Starting laptop camera test...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera failed")
    exit()

print("Camera opened")

while True:
    ret, frame = cap.read()

    if not ret:
        print("NO FRAME")
        break

    cv2.imshow("Laptop Camera LIVE", frame)

    key = cv2.waitKey(1)

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()