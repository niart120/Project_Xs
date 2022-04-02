import rngtool
import calc
import cv2
import time
from xorshift import Xorshift
import heapq

imgpath = "./trainer/spearpillar/eye.png"

def firstspecify():
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 935,505,25,30)
    prng = rngtool.recov(blinks, intervals)

    waituntil = time.perf_counter()
    diff = round(waituntil-offset_time)
    prng.getNextRandSequence(diff)

    state = prng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

def reidentify():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    imgpath = "./trainer/halloforigin/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    observed_blinks, observed_intervals, offset_time = rngtool.tracking_blink(player_eye, 925, 480, 30, 40,size=20)
    #reidentified_rng = rngtool.reidentifyByBlinks(Xorshift(*state), observed_blinks)
    reidentified_rng = rngtool.reidentifyByIntervalsNoisy(Xorshift(*state), observed_intervals)
    if reidentified_rng is None:
        print("couldn't reidentify state.")
        return

    waituntil = time.perf_counter()
    diff = int(-(-(waituntil-offset_time)//1))
    print(diff, waituntil-offset_time)
    reidentified_rng.advances(max(diff,0))

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    #timecounter reset
    advances = 0
    waituntil = time.perf_counter()
    time.sleep(diff - (waituntil - offset_time))

    while True:
        advances += 1
        r = reidentified_rng.next()

        waituntil += 1.017        
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)
        print(f"advances:{advances}, blink:{hex(r&0xF)}")

def stationary_timeline():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    imgpath = "./trainer/halloforigin/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    observed_blinks, observed_intervals, offset_time = rngtool.tracking_blink(player_eye, 925, 480, 30, 40,size=20)
    reidentified_rng = rngtool.reidentifyByIntervalsNoisy(Xorshift(*state), observed_intervals)

    if reidentified_rng is None:
        print("couldn't reidentify state.")
        return

    waituntil = time.perf_counter()
    diff = int(-(-(waituntil-offset_time)//1))
    reidentified_rng.advances(max(diff,0))

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    queue = []
    #timecounter reset
    advances = 1
    waituntil = time.perf_counter()
    time.sleep(diff - (waituntil - offset_time))
    #timeline prepare
    blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
    heapq.heappush(queue, (waituntil+blink_int,1))

    #_ = reidentified_rng.next()
    heapq.heappush(queue, (waituntil+1.017,0))

    while queue:
        advances += 1
        w, q = heapq.heappop(queue)
        next_time = w - time.perf_counter() or 0
        if next_time>0:
            time.sleep(next_time)

        if q==0:
            r = reidentified_rng.next()
            print(f"advances:{advances}, blink:{hex(r&0xF)}")
            heapq.heappush(queue, (w+1.017, 0))
        else:
            blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
            heapq.heappush(queue, (w+blink_int, 1))
            print(f"advances:{advances}, interval:{blink_int}")
if __name__ == "__main__":
    #firstspecify()
    #reidentify()
    stationary_timeline()
