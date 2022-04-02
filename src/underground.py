import rngtool
import calc
import cv2
import time
from xorshift import Xorshift

def expr():
    player_eye = cv2.imread("./trainer/secretbase/eye.png", cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 870, 680, 85, 90)
    prng = rngtool.recov(blinks, intervals)

    waituntil = time.perf_counter()
    diff = round(waituntil-offset_time)
    prng.getNextRandSequence(diff)

    state = prng.getState()
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))

    #timecounter reset
    advances = 0
    wild_prng = Xorshift(*prng.getState())
    wild_prng.getNextRandSequence(1)

    advances = 0

    for i in range(100):
        advances += 1
        r = prng.next()
        wild_r = wild_prng.next()

        waituntil += 1.018

        print(f"advances:{advances}, blinks:{hex(r&0xF)}")        
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

def firstspecify():
    player_eye = cv2.imread("./trainer/secretbase/eye.png", cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 870, 680, 85, 90,cameraID=1)
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

    player_eye = cv2.imread("./trainer/underground/north/eye.png", cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    npcnum = 1

    _, intervals, offset_time = rngtool.tracking_blink(player_eye, 925, 520, 35, 35, th = 0.8, size=7, cameraID=1)
    reidentified_rng = rngtool.reidentifyByIntervals(Xorshift(*state), intervals, npc=npcnum)
    
    waituntil = time.perf_counter()
    diff = round(waituntil-offset_time)+1
    reidentified_rng.getNextRandSequence(diff)

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print()
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])
    print()

    #timecounter reset
    advances = 0

    delay = 2
    wild_prng = Xorshift(*reidentified_rng.getState())
    wild_prng.getNextRandSequence(1+delay)

    advances = 0

    while True:
        for _ in range(1+npcnum):
            advances += 1
            r = reidentified_rng.next()
            wild_r = wild_prng.next()
            print(f"advances:{advances}, blinks:{hex(r&0xF)}", end=" ")
        print()

        waituntil += 1.018       
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

def reidentifyInSecretBase():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    imgpath = "./trainer/secretbase/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, observed_intervals, offset_time = rngtool.tracking_blink(player_eye, 870, 680, 85, 90, size=7, cameraID=1)
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

if __name__ == "__main__":
    #firstspecify()
    #reidentify()
    reidentifyInSecretBase()