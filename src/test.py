import rngtool
import cv2
import time
from xorshift import Xorshift
import heapq

def firstspecify():
    imgpath = "./trainer/ramanas/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 925, 750, 30, 35, cameraID=1)
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

    imgpath = "./gradon/eye.png"
    poke_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if poke_eye is None:
        print("path is wrong")
        return
    

    rawintervals, offset_time = rngtool.tracking_poke_blink(poke_eye, 990, 540, 30, 55, th=0.35, size=5, cameraID=1)
    rng, next_pl_blink, next_pk_blink = rngtool.reidentify_by_pokeblink(Xorshift(*state), rawintervals, eps=0.1)

    if rng is None:
        print("could not reidentify the state")
        return

    state = rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    advances = 0
    queue = []
    #timeline prepare
    #player blink
    rng.advances(2)
    advances += 2
    heapq.heappush(queue, (offset_time+next_pl_blink+1.017, 0))
    #pokemon blink
    heapq.heappush(queue, (offset_time+next_pk_blink, 1))

    while queue:
        advances += 1
        w, q = heapq.heappop(queue)
        next_time = w - time.perf_counter() or 0
        if next_time>0:
            time.sleep(next_time)

        if q==0:
            r = rng.next()
            print(f"advances:{advances}, blink:{hex(r&0xF)}")
            heapq.heappush(queue, (w+1.017, 0))
        else:
            blink_int = rng.range(3.0, 12.0) + 0.285
            heapq.heappush(queue, (w+blink_int, 1))
            print(f"advances:{advances}, interval:{blink_int}")

def reidentify_player():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    plimgpath = "./trainer/strangespace/eye.png"
    plimg = cv2.imread(plimgpath, cv2.IMREAD_GRAYSCALE)
    plroi = (925, 500, 35, 35)

    blinks, observed_intervals, offset_time = rngtool.tracking_blink(plimg, 925, 740, 30, 40, th=0.8, size=8, cameraID=1)

    reidentified_rng, next_pk_blink = rngtool.reidentifyByIntervalsNoisy(Xorshift(*state), observed_intervals)

    if reidentified_rng is None:
        print("couldn't reidentify state.")
        return

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    advances = 0
    #timeline prepare
    queue = []
    heapq.heappush(queue, (offset_time+61/60,0))
    heapq.heappush(queue, (offset_time+next_pk_blink,1))

    while True:
        advances += 1
        w, q = heapq.heappop(queue)
        next_time = w - time.perf_counter() or 0
        if next_time>0:
            time.sleep(next_time)

        if q==0:
            r = reidentified_rng.next()
            print(f"advances:{advances}, blink:{hex(r&0xF)}")
            heapq.heappush(queue, (w+61/60, 0))
        else:
            blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
            heapq.heappush(queue, (w+blink_int, 1))
            print(f"advances:{advances}, interval:{blink_int}")

if __name__ == "__main__":
    #firstspecify()
    reidentify_player()