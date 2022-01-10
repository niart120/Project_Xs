"""[summary]

"""
from typing import List
from typing import Tuple
import time
import cv2
from xorshift import Xorshift
import calc

IDLE = 0xFF
SINGLE = 0xF0
DOUBLE = 0xF1

def randrange(r,mi,ma):
    t = (r & 0x7fffff) / 8388607.0
    return t * mi + (1.0 - t) * ma

def tracking_blink(img, roi_x, roi_y, roi_w, roi_h, th = 0.9, size = 40)->Tuple[List[int],List[int],float]:
    """measuring the type and interval of player's blinks

    Returns:
        blinks:List[int],intervals:list[int],offset_time:float: [description]
    """

    eye = img

    video = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    video.set(cv2.CAP_PROP_BUFFERSIZE,1)

    state = IDLE
    blinks = []
    intervals = []
    prev_time = time.perf_counter()

    prev_roi = None
    debug_txt = ""

    offset_time = 0

    # 瞬きの観測
    while len(blinks)<size or state!=IDLE:
        _, frame = video.read()
        time_counter = time.perf_counter()
        roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():
            continue

        prev_roi = roi
        res = cv2.matchTemplate(roi,eye,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)

        cv2.imshow("",roi)
        cv2.waitKey(1)

        if 0.01<match<th:
            if state==IDLE:
                blinks.append(0)
                interval = (time_counter - prev_time)/1.018
                interval_round = round(interval)
                intervals.append(interval_round)

                if len(intervals)==size:
                    offset_time = time_counter

                #check interval 
                check = " " if abs(interval-interval_round)<0.2 else "*"
                debug_txt = f"{interval}"+check
                state = SINGLE
                prev_time = time_counter
            elif state==SINGLE:
                #doubleの判定
                if time_counter - prev_time>0.3:
                    blinks[-1] = 1
                    debug_txt = debug_txt+"d"
                    state = DOUBLE
            elif state==DOUBLE:
                pass

        if state!=IDLE and time_counter - prev_time>0.7:
            state = IDLE
            print(debug_txt, len(blinks))
    cv2.destroyAllWindows()
    return (blinks, intervals, offset_time)

def tracking_poke_blink(img, roi_x, roi_y, roi_w, roi_h, size = 60)->Tuple[List[int],List[int],float]:
    """measuring the type and interval of pokemon's blinks

    Returns:
        intervals:list[int],offset_time:float: [description]
    """

    eye = img
    
    video = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    video.set(cv2.CAP_PROP_BUFFERSIZE,1)

    state = IDLE

    intervals = []
    prev_roi = None
    prev_time = time.perf_counter()


    # 瞬きの観測
    while len(intervals)<size:
        _, frame = video.read()
        time_counter = time.perf_counter()

        roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():
            continue
        prev_roi = roi
        cv2.imshow("",roi)
        cv2.waitKey(1)
        res = cv2.matchTemplate(roi,eye,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)

        if 0.4<match<0.85:
            if state==IDLE:
                interval = (time_counter - prev_time)
                print(interval)
                intervals.append(interval)
                state = SINGLE
                prev_time = time_counter
            elif state==SINGLE:
                pass
        if state!=IDLE and time_counter - prev_time>0.7:
            state = IDLE
    cv2.destroyAllWindows()
    video.release()
    return intervals

def recov(blinks:List[int],rawintervals:List[int])->Xorshift:
    """
    Recover the xorshift from the type and interval of blinks.

    Args:
        blinks (List[int]):
        intervals (List[int]):

    Returns:
        List[int]: internalstate
    """
    intervals = rawintervals[1:]
    advanced_frame = sum(intervals)
    states = calc.reverseStates(blinks, intervals)
    prng = Xorshift(*states)
    states = prng.getState()

    #validation check
    expected_blinks = [r&0xF for r in prng.getNextRandSequence(advanced_frame) if r&0b1110==0]
    paired = list(zip(blinks,expected_blinks))
    print(blinks)
    print(expected_blinks)
    #print(paired)
    assert all([o==e for o,e in paired])

    result = Xorshift(*states)
    result.getNextRandSequence(advanced_frame)
    return result

def reidentifyByBlinks(rng:Xorshift, observed_blinks:List[int], npc = 0, search_max=10**6, search_min=0)->Xorshift:
    if search_max<search_min:
        search_min, search_max = search_max, search_min
    search_range = search_max - search_min
    observed_len = len(observed_blinks)
    if 2**observed_len < search_range:
        return None

    for d in range(1+npc):
        identify_rng = Xorshift(*rng.getState())
        rands = [(i, r&0xF) for i,r in list(enumerate(identify_rng.getNextRandSequence(search_max)))[d::1+npc]]
        blinkrands = [(i, r) for i,r in rands if r&0b1110==0]

        #prepare
        expected_blinks_lst = []
        expected_blinks = 0
        lastblink_idx = -1
        mask = (1<<observed_len)-1
        for idx, r in blinkrands[:observed_len]:
            lastblink_idx = idx

            expected_blinks <<= 1
            expected_blinks |= r

        expected_blinks_lst.append((lastblink_idx, expected_blinks))

        for idx, r in blinkrands[observed_len:]:
            lastblink_idx = idx

            expected_blinks <<= 1
            expected_blinks |= r
            expected_blinks &= mask

            expected_blinks_lst.append((lastblink_idx, expected_blinks))

        #search
        search_blinks = calc.list2bitvec(observed_blinks)
        result = Xorshift(*rng.getState())
        for idx, blinks in expected_blinks_lst:
            if search_blinks==blinks and search_min <= idx:
                print(f"found  at advances:{idx}, d={d}")
                result.getNextRandSequence(idx)
                return result

    return None

def recovByMunchlax(rawintervals:List[float])->Xorshift:
    """Recover the xorshift from the interval of Munchlax blinks.

    Args:
        rawintervals (List[float]): [description]

    Returns:
        Xorshift: [description]
    """
    advances = len(rawintervals)
    intervals = [interval+0.048 for interval in rawintervals]#観測結果のずれを補正
    intervals = intervals[1:]#最初の観測結果はノイズなのでそれ以降を使う
    states = calc.reverseStatesByMunchlax(intervals)

    prng = Xorshift(*states)
    states = prng.getState()

    #validation check
    expected_intervals = [randrange(r,100,370)/30 for r in prng.getNextRandSequence(advances)]

    paired = list(zip(intervals,expected_intervals))
    #print(paired)

    assert all([abs(o-e)<0.1 for o,e in paired])
    result = Xorshift(*states)
    result.getNextRandSequence(len(intervals))
    return result