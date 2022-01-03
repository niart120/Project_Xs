import rngtool
import calc
import cv2
import time
from xorshift import Xorshift

imgpath = "./trainer/trophygarden/eye.png"

def expr():
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 930, 510, 30, 30)
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
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 930, 510, 30, 30)
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

    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    observed_blinks, _, offset_time = rngtool.tracking_blink(player_eye, 930, 505, 30, 30,size=20)
    reidentified_rng = rngtool.reidentifyByBlinks(Xorshift(*state), observed_blinks)
    
    waituntil = time.perf_counter()
    diff = -((waituntil-offset_time)//(-1))
    reidentified_rng.getNextRandSequence(diff)

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    #timecounter reset
    advances = 0
    wild_prng = Xorshift(*reidentified_rng.getState())
    isUnown = False
    wild_prng.getNextRandSequence(2+isUnown)

    advances = 0

    while True:
        advances += 1
        r = reidentified_rng.next()
        wild_r = wild_prng.next()

        waituntil += 1.018

        print(f"advances:{advances}, blinks:{hex(r&0xF)}")        
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

if __name__ == "__main__":
    #firstspecify()
    reidentify()