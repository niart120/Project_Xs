from typing import List, Tuple
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

def tracking_blink(img, roi_x, roi_y, roi_w, roi_h)->Tuple[List[int],List[int],float]:
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
    prev_match = 0
    prev_time = 0

    prev_roi = None
    debug_txt = ""

    # 瞬きの観測
    while len(blinks)<40 or state!=IDLE:
        ret, frame = video.read()
        time_counter = time.perf_counter()
        unix_time = time.time()
        roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():continue
        prev_roi = roi        
        res = cv2.matchTemplate(roi,eye,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)
        cv2.imshow("",roi)
        cv2.waitKey(1)
        if 0.01<match<0.85:
            if state==IDLE:
                blinks.append(0)
                interval = (time_counter - prev_time)/1.018
                interval_round = round(interval)
                intervals.append(interval_round)

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
            print(debug_txt)
    cv2.destroyAllWindows()
    return (blinks, intervals)

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

    offset_time = 0

    # 瞬きの観測
    while len(intervals)<size:
        ret, frame = video.read()
        time_counter = time.perf_counter()

        roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():continue
        prev_roi = roi

        res = cv2.matchTemplate(roi,eye,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)

        if 0.4<match<0.85:
            if len(intervals)==1:
                offset_time = unix_time
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
    result.getNextRandSequence(len(intervals))
    return result

def recovByMunchlax(rawintervals:List[float])->Xorshift:
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