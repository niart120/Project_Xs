import rngtool
import calc
import cv2
import time
from xorshift import Xorshift

def expr():
    player_eye = cv2.imread("./trainer/ruins/eye.png", cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 910, 485, 50, 60)
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
    #
    while True:
        advances += 1
        r = prng.next()
        wild_r = wild_prng.next()

        waituntil += 1

        print(f"advances:{advances}, blinks:{hex(r&0xF)}")        
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

if __name__ == "__main__":
    expr()