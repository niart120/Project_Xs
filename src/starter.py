import rngtool
import calc
import cv2
import time
from xorshift import Xorshift
import heapq

def firstspecify():
    imgpath = "./trainer/home/eye_blur.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 905, 750, 55, 55)
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

    imgpath = "./barry/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    observed_blinks, _, offset_time = rngtool.tracking_blink(player_eye, 1065, 490, 30, 35,size=20)
    reidentified_rng = rngtool.reidentifyByBlinks(Xorshift(*state), observed_blinks,npc=1)
    if reidentified_rng is None:
        print("couldn't reidentify state.")
        return

    waituntil = time.perf_counter()
    diff = int(-(-(waituntil-offset_time)//1))
    print(diff, waituntil-offset_time)
    reidentified_rng.advances(max(diff,0)*2)

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    advances = 0
    waituntil = time.perf_counter()
    time.sleep(diff - (waituntil - offset_time))

    while True:
        waituntil += 1.018       
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)
        #player/barry
        advances += 1
        r = reidentified_rng.next()
        print(f"advances:{advances}, blinks:{hex(r&0xF)}", end=" ")
        #barry/player
        advances += 1
        r = reidentified_rng.next()
        print(f"advances:{advances}, blinks:{hex(r&0xF)}", end=" ")
        print()

def starter_timeline():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]

    imgpath = "./barry/eye.png"
    player_eye = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    observed_blinks, _, offset_time = rngtool.tracking_blink(player_eye, 1065, 490, 30, 35,size=20)
    reidentified_rng = rngtool.reidentifyByBlinks(Xorshift(*state), observed_blinks,npc=1)
    if reidentified_rng is None:
        print("couldn't reidentify state.")
        return

    waituntil = time.perf_counter()
    diff = int(-(-(waituntil-offset_time)//1))
    print(waituntil-offset_time)
    reidentified_rng.advances(max(diff,0)*2)

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    #timecounter reset
    advances = 0
    waituntil = time.perf_counter()
    time.sleep(diff - (waituntil - offset_time))
    print("next message 'I heard them say professor...'")

    for _ in [0]*20:
        waituntil += 1.018
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)
        #player/barry
        advances += 1
        r = reidentified_rng.next()
        print(f"advances:{advances}, blinks:{hex(r&0xF)}", end=" ")
        #barry/player
        advances += 1
        r = reidentified_rng.next()
        print(f"advances:{advances}, blinks:{hex(r&0xF)}", end=" ")
        print()

    #advances(reference:https://github.com/Lincoln-LM/Project_Xs/blob/main/configs/config_starter.json)
    advances += 41 #"advance_delay"
    reidentified_rng.advances(41)
    waituntil = time.perf_counter()
    print("press A")
    queue = []
    
    #first(?) starly
    advances += 1
    #blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
    blink_int = reidentified_rng.rangefloat(3,12) + 0.285
    heapq.heappush(queue, waituntil+blink_int)
    
    #second(?) starly
    advances += 1
    #blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
    blink_int = reidentified_rng.rangefloat(3,12) + 0.285
    heapq.heappush(queue, waituntil+blink_int)
    print("next massage:'What's going on?!'")
    for _ in range(4):
        advances += 1
        w = heapq.heappop(queue)
        next_time = w - time.perf_counter() or 0
        if next_time>0:
            time.sleep(next_time)

        #blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
        blink_int = reidentified_rng.rangefloat(3,12) + 0.285
        heapq.heappush(queue, w+blink_int)
        print(f"advances:{advances}, interval:{blink_int}")

    #advances(reference:https://github.com/Lincoln-LM/Project_Xs/blob/main/configs/config_starter.json)
    advances += 49 #"advance_delay_2"
    reidentified_rng.advances(49)
    print("press A")

    #advance(+1 when select sterter)
    advances += 1
    while queue:
        advances += 1
        w = heapq.heappop(queue)
        next_time = w - time.perf_counter() or 0
        if next_time>0:
            time.sleep(next_time)

        #blink_int = reidentified_rng.range(3.0, 12.0) + 0.285
        blink_int = reidentified_rng.rangefloat(3,12) + 0.285

        heapq.heappush(queue, w+blink_int)
        print(f"advances:{advances}, interval:{blink_int}")


if __name__ == "__main__":
    #firstspecify()
    #reidentify()
    starter_timeline()