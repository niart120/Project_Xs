import cv2
import time

def main():
    eye = cv2.imread("E:/documents/VSCodeWorkspace/Project_Xs/src/debug/naetoru.png",cv2.IMREAD_GRAYSCALE)
    #video = cv2.VideoCapture("E:/documents/VSCodeWorkspace/Project_Xs/src/debug/naetoru_blink.mp4")
    video = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    
    IDLE = 0xFF
    CLOSING = 0x0F
    state = IDLE
    intervals = []
    prev_time = 0

    offset_time = 0
    fc = 0
    prev_fc = 0

    prev_roi = None

    # 瞬きの観測
    while len(intervals)<3000:
        ret, frame = video.read()
        if not ret:break

        time_counter = time.perf_counter()
        unix_time = time.time()
        x,y = 830,460
        box_w,box_h = 120, 160
        roi = cv2.cvtColor(frame[y:y+box_h,x:x+box_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():continue
        prev_roi = roi
        fc += 1

        res = cv2.matchTemplate(roi,eye,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)

        if 0.4<match<0.9:
            if len(intervals)==0:
                offset_time = unix_time
            if state==IDLE:
                interval = (fc-prev_fc)
                interval_round = round(interval)
                intervals.append(interval_round)

                print(fc-prev_fc)
                prev_fc = fc

                state = CLOSING
                prev_time = time_counter

            elif state==CLOSING:
                if time_counter - prev_time>0.5:
                    state = IDLE
        if time_counter - prev_time>0.5:
            state = IDLE

    cv2.destroyAllWindows()
    print(intervals)
if __name__ == "__main__":
    main()