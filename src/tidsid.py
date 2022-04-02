import rngtool
import calc
import cv2
import time
from xorshift import Xorshift

def randrange(r,mi,ma):
    t = (r & 0x7fffff) / 8388607.0
    return t * mi + (1.0 - t) * ma

def getids(r):
    g7tid = ((r%0xFFFFFFFF+0x80000000)&0xFFFFFFFF)%1000000
    tid,sid = r&0xFFFF, r>>16
    return g7tid, tid, sid

def expr():
    munch_eye = cv2.imread("./munchlax/eye.png", cv2.IMREAD_GRAYSCALE)
    if munch_eye is None:
        print("path is wrong")
        return
    gombe_intervals = rngtool.tracking_poke_blink(munch_eye, 730, 670, 50, 60)

    interval_prng, offset_time = rngtool.recovByMunchlax(gombe_intervals)
    state = interval_prng.getState()

    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    #timecounter reset
    advances = 0
    id_prng = Xorshift(*interval_prng.getState())
    id_prng.next()
    
    waituntil = time.perf_counter()
    #ID予測開始
    while True:
        advances += 1
        #interval = interval_prng.rangefloat(3.0,12.0) + 0.285
        interval = interval_prng.range(3.0,12.0) + 0.285
        waituntil += interval

        id_r = id_prng.next()
        g7tid, tid, sid = getids(id_r)
        print(f"advances:{advances}, g7tid:{g7tid}, tid:{hex(tid)}, sid:{hex(sid)}")
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

def reidentify():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]
    munch_eye = cv2.imread("./munchlax/eye.png", cv2.IMREAD_GRAYSCALE)
    if munch_eye is None:
        print("path is wrong")
        return
    gombe_intervals, offset_time = rngtool.tracking_poke_blink(munch_eye, 730, 670, 50, 60, size=5)

    interval_prng = rngtool.reidentifyByMunchlax(Xorshift(*state),gombe_intervals)
    state = interval_prng.getState()

    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    #timecounter reset
    advances = 0
    id_prng = Xorshift(*interval_prng.getState())
    id_prng.next()
    
    waituntil = time.perf_counter()
    #ID予測開始
    while True:
        advances += 1
        interval = interval_prng.range(3.0,12.0) + 0.285
        waituntil += interval

        id_r = id_prng.next()
        g7tid, tid, sid = getids(id_r)
        print(f"advances:{advances}, g7tid:{g7tid}, tid:{hex(tid)}, sid:{hex(sid)}")
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

def test():
    """ゴンベの瞬きがfloat rangeによって生成されているかを検証します
    """
    munch_eye = cv2.imread("E:/documents/VSCodeWorkspace/Project_Xs/munchlax/eye.png", cv2.IMREAD_GRAYSCALE)
    gombe_intervals, _ = rngtool.tracking_poke_blink(munch_eye, 730, 670, 50, 60)
    
    print("input any key to continue...")
    input()

    blinks, intervals, offset = rngtool.tracking_blink()
    prng = rngtool.recov(blinks,intervals)

    print("input trainer ID")
    playerid = int(input())

    for i in range(10000):
        r = prng.prev()
        g7tid = ((r%0xFFFFFFFF+0x80000000)&0xFFFFFFFF)%1000000
        tid,sid = r&0xFFFFFFFF, r>>16
        if g7tid==playerid:
            print(f"backwarding {i},", hex(tid),hex(sid))
            break
    
    randlist = prng.getPrevRandSequence(100)
    expected_intervals = [randrange(r,100.0,370.0)/30.0 for r in randlist]
    
    print(f"observed:{gombe_intervals[::-1]}")
    print(f"expected:{expected_intervals}")

def main():
    blinks, intervals, offset = rngtool.tracking_blink()
    prng = rngtool.recov(blinks,intervals)
    print(f"state:{prng.getState()}")
    print("input trainer ID")
    playerid = int(input())

    for i in range(10000):
        r = prng.prev()
        g7tid = ((r%0xffffffff+0x80000000)&0xFFFFFFFF)%1000000
        tid,sid = r&0xFFFFFFFF, r>>16
        if g7tid==playerid:
            print(f"backwarding {i},", hex(tid),hex(sid))
            break
    randlist = prng.getPrevRandSequence(100)
    expected_intervals = [randrange(r,100.0,370.0)/30.0 for r in randlist]
    
    print(f"expected:{expected_intervals}")

if __name__ == "__main__":
    expr()
    #reidentify()