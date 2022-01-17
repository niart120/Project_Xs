"""
this program is experimental.
"""

import rngtool
import calc
import cv2
import time
from xorshift import Xorshift
import heapq

imgpath = "./trainer/fullmoon/eye.png"

def firstspecify():
    imgpath = "./trainer/secretbase/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 870, 680, 85, 90)
    prng = rngtool.recov(blinks, intervals, )

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
    plimgpath = "./trainer/fullmoon/eye.png"
    plimg = cv2.imread(plimgpath, cv2.IMREAD_GRAYSCALE)
    plroi = (925, 500, 35, 35)

    pkimgpath = "./cresselia/eye.png"
    pkimg = cv2.imread(pkimgpath, cv2.IMREAD_GRAYSCALE)
    pkroi = (805, 475, 20, 30)
    blinks, observed_intervals, offset_time = rngtool.simultaneous_tracking(plimg, plroi, pkimg, pkroi, pkth = 0.999185, size = 8)

    reidentified_rng = rngtool.reidentifyByIntervals(Xorshift(*state), observed_intervals, th=2, search_max=10**5)
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

def reidentifyInSecretBase():
    """reidentify xorshift internal state in the cresselia's room
    note: this function is a bit unreliable since it is difficult to track the blinks of cresselia.
    
    """
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    imgpath = "./trainer/secretbase/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, observed_intervals, offset_time = rngtool.tracking_blink(player_eye, 870, 680, 85, 90, size=7)
    reidentified_rng = rngtool.reidentifyByIntervals(Xorshift(*state), observed_intervals, npc=0)
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

def cresselia_timeline():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    plimgpath = "./trainer/fullmoon/eye.png"
    plimg = cv2.imread(plimgpath, cv2.IMREAD_GRAYSCALE)
    plroi = (925, 500, 35, 35)

    pkimgpath = "./cresselia/eye.png"
    pkimg = cv2.imread(pkimgpath, cv2.IMREAD_GRAYSCALE)
    pkroi = (805, 475, 20, 30)
    blinks, observed_intervals, offset_time = rngtool.simultaneous_tracking(plimg, plroi, pkimg, pkroi, pkth = 0.999185, size = 4)

    reidentified_rng = rngtool.reidentifyByIntervals(Xorshift(*state), observed_intervals, th=1, search_max=1*10**3, search_min=0)
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

    advances = 1
    waituntil = time.perf_counter()
    time.sleep(diff - (waituntil - offset_time))
    #timeline prepare
    queue = []
    blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
    #blink_int = reidentified_rng.rangefloat(3,12) + 0.285
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
            #blink_int = reidentified_rng.rangefloat(3,12) + 0.285

            heapq.heappush(queue, (w+blink_int, 1))
            print(f"advances:{advances}, interval:{blink_int}")

if __name__ == "__main__":
    #note:
    #1. specify internal state with firstspecify() (secretbase is better place)
    #2. search target on pokefinder
    #3. advance rng (fullmoon island exterior is fast, about +250/s)
    #4. enter the cresselia's room 2000 advances before the target, and reidentify state with cresselia_timeline()
    #5. 

    #firstspecify()
    #reidentifyInSecretBase()
    cresselia_timeline()
