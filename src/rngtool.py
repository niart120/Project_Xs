"""[summary]

"""
from typing import List
from typing import Tuple
import time
import cv2
from xorshift import Xorshift
import calc
from collections import Counter
import math

IDLE = 0xFF
SINGLE = 0xF0
DOUBLE = 0xF1

def randrange(r,mi,ma):
    t = (r & 0x7fffff) / 8388607.0
    return t * mi + (1.0 - t) * ma

def tracking_blink(img, roi_x, roi_y, roi_w, roi_h, th = 0.9, size = 40, cameraID = 0)->Tuple[List[int],List[int],float]:
    """measuring the type and interval of player's blinks

    Returns:
        blinks:List[int], intervals:list[int], offset_time:float
    """

    eye = img

    video = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
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

    # observe blinks
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
                interval = (time_counter - prev_time)/1.017
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

def tracking_poke_blink(img, roi_x, roi_y, roi_w, roi_h, th = 0.85, size = 64, cameraID = 0)->Tuple[List[float], float]:
    """measuring the interval of pokemon's blinks

    Returns:
        intervals:list[float]
        offset_time:
    """

    eye = img
    
    video = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    video.set(cv2.CAP_PROP_BUFFERSIZE,1)

    state = IDLE

    intervals = []
    prev_roi = None
    prev_time = time.perf_counter()

    offset_time = 0

    # observe blinks
    count = 0
    while len(intervals)<size:
        _, frame = video.read()
        time_counter = time.perf_counter()

        roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():
            continue
        prev_roi = roi
        cv2.imshow("",cv2.resize(roi, (roi_w*2, roi_h*2)))
        cv2.waitKey(1)
        res = cv2.matchTemplate(roi,eye,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)
        #print(match)
        if 0.1<match and match<th:
            if state==IDLE:
                interval = (time_counter - prev_time)
                count += 1
                print(f"blinks:{count}/{size}, interval:{interval}")
                intervals.append(interval)
                state = SINGLE
                prev_time = time_counter

                if len(intervals)==size:
                    offset_time = time_counter
            elif state==SINGLE:
                pass
        if state!=IDLE and time_counter - prev_time>0.7:
            state = IDLE
    cv2.destroyAllWindows()
    video.release()

    return intervals, offset_time

def simultaneous_tracking(plimg, plroi:Tuple[int,int,int,int], pkimg, pkroi:Tuple[int,int,int,int], plth=0.88, pkth=0.999185, size=8)->Tuple[List[int],List[int],float]:
    """measuring type/intervals of player's blinks  and the interval of pokemon's blinks
        note: this methods is very unstable. it not recommended to use.
    Returns:
        intervals:list[int],offset_time:float: [description]
    """
    video = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    video.set(cv2.CAP_PROP_BUFFERSIZE,1)

    pl_state = IDLE
    pk_state = IDLE
    blinks = []
    intervals = []
    pl_prev = time.perf_counter()
    pk_prev = time.perf_counter()

    prev_roi = None
    debug_txt = ""

    offset_time = 0

    blinkcounter = 0

    # observe blinks
    while len(blinks)<size or pl_state!=IDLE:
        _, frame = video.read()
        time_counter = time.perf_counter()

        #player eye
        roi_x,roi_y,roi_w,roi_h = plroi
        roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)
        if (roi==prev_roi).all():
            continue

        prev_roi = roi
        res = cv2.matchTemplate(roi,plimg,cv2.TM_CCOEFF_NORMED)
        _, match, _, _ = cv2.minMaxLoc(res)

        #cv2.imshow("pl",roi)

        if 0.01<match<plth:
            if pl_state==IDLE:
                blinks.append(0)
                interval = (time_counter - pl_prev)/1.017
                interval_round = round(interval)
                interval_corrected = interval_round + blinkcounter
                blinkcounter = 0#reset blinkcounter
                intervals.append(interval_corrected)

                if len(intervals)==size:
                    offset_time = time_counter

                #check interval 
                check = " " if abs(interval-interval_round)<0.2 else "*"
                debug_txt = f"{interval}"+check
                pl_state = SINGLE
                pl_prev = time_counter
            elif pl_state==SINGLE:
                #double
                if time_counter - pl_prev>0.3:
                    blinks[-1] = 1
                    debug_txt = debug_txt+"d"
                    pl_state = DOUBLE
            elif pl_state==DOUBLE:
                pass

        if pl_state!=IDLE and time_counter - pl_prev>0.7:
            pl_state = IDLE
            print(debug_txt, len(blinks))

        if pk_state==IDLE:
            #poke eye
            roi_x,roi_y,roi_w,roi_h = pkroi
            roi = cv2.cvtColor(frame[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w],cv2.COLOR_RGB2GRAY)

            res = cv2.matchTemplate(roi,pkimg,cv2.TM_CCORR_NORMED)#CCORR might be better?
            _, match, _, _ = cv2.minMaxLoc(res)
            cv2.imshow("pk",roi)
            cv2.waitKey(1)
            if 0.4<match<pkth:
                #print("poke blinked!")
                blinkcounter += 1
                pk_prev = time_counter
                pk_state = SINGLE

        if pk_state!=IDLE and time_counter - pk_prev>0.7:
            pk_state = IDLE
        
    cv2.destroyAllWindows()
    print(intervals)
    return (blinks, intervals, offset_time)

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
    """reidentify Xorshift state by the type of observed blinks.

    Args:
        rng (Xorshift): identified rng
        observed_blinks (List[int]): 
        npc (int, optional): num of npcs. Defaults to 0.
        search_max (int, optional): . Defaults to 10**6.
        search_min (int, optional): . Defaults to 0.

    Returns:
        Xorshift: reidentified rng
    """
    
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

def reidentifyByIntervals(rng:Xorshift, rawintervals:List[int], npc = 0, th = 0, search_max=10**6, search_min=0)->Xorshift:
    """reidentify Xorshift state by intervals of observed blinks. 
    This method is faster than "reidentifyByBlinks" in most cases since it can be reidentified by less blinking.

    Args:
        rng (Xorshift): [description]
        rawintervals (List[int]): list of intervals of blinks. 7 or more are recommended.
        npc (int, optional): [description]. Defaults to 0.
        search_max ([type], optional): [description]. Defaults to 10**6.
        search_min (int, optional): [description]. Defaults to 0.

    Returns:
        Xorshift: [description]
    """
    intervals = rawintervals[1:]
    if search_max<search_min:
        search_min, search_max = search_max, search_min
    search_range = search_max - search_min
    observed_len = sum(intervals)+1

    for d in range(1+npc):
        identify_rng = Xorshift(*rng.getState())
        blinkrands = [(i, int((r&0b1110)==0)) for i,r in list(enumerate(identify_rng.getNextRandSequence(search_max)))[d::1+npc]]

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

        #search preparation
        search_blinks = 1
        for i in intervals:
            search_blinks <<= i
            search_blinks |= 1

        #search
        result = Xorshift(*rng.getState())
        distlst = []
        for idx, blinks in expected_blinks_lst:
            #check by hamming distance
            distance = bin(search_blinks^blinks).count("1")
            distlst.append(distance)
            isSame = distance<=th
            if isSame and search_min <= idx:
                print(f"found  at advances:{idx}, d={d}, hamming={distance}")
                result.getNextRandSequence(idx)
                return result
        c = Counter(distlst)
        print(sorted(c.items()))

    return None

def reidentifyByIntervalsNoisy(rng:Xorshift, rawintervals:List[int],search_max = 10**5, search_min = 0)->Tuple[Xorshift,float]:
    blinktime = 0.285
    
    pl_intervals = tuple(rawintervals[1:])
    n = len(pl_intervals)

    #search
    search_range = search_max-search_min
    rng = Xorshift(*rng.getState())
    rng.advances(search_min)

    gen_range = search_range+sum(pl_intervals)+1
    #ポケモンの瞬き間隔の前計算
    pk_intervals = [randrange(r,3,12)+blinktime for r in Xorshift(*rng.getState()).getNextRandSequence(gen_range)]
    
    #瞬きが生じるような乱数値のindexlistの作成
    blink_indices = [i for (i,r) in enumerate(Xorshift(*rng.getState()).getNextRandSequence(search_range)) if r&0b1110 == 0]
    indices_set = set(blink_indices)

    for i in range(len(blink_indices)):
        starting = 0.0
        while starting < 12.0:
            pk_timer = starting
            offset = 0
            t = 0.0
            prev_idx = blink_indices[i]
            j = prev_idx
            expected = []
            while len(expected)<n:
                t += 61/60
                j += 1
                if pk_timer<t:#ポケモンの瞬き発生時
                    pk_timer += pk_intervals[j]
                    j += 1
                    offset += 1
                if j in indices_set:#主人公の瞬き発生時
                    intvl = j - prev_idx - offset
                    expected.append(intvl)
                    offset = 0
                    prev_idx = j
            expected = tuple(expected)
            if pl_intervals==expected:
                found_idx = search_min+j
                print(f"found at:{found_idx}, t = {t}, pk_timer = {pk_timer}")
                next_pk_blink = pk_timer-t
                result = Xorshift(*rng.getState())
                result.advances(found_idx+1)
                return result, next_pk_blink
 
            starting += 0.1
    
    return None, None

def previous(rng:Xorshift, rawintervals:List[int], search_max=10**5, search_min=0)->Xorshift:
    """Reidentify Xorshift state via intervals with noise in the background"""


    intervals = rawintervals[1:]
    blink_bools = [True]
    for interval in intervals:
        blink_bools.extend([False]*(interval-1))
        blink_bools.append(True)
    reident_time = len(blink_bools)
    possible_length = int(reident_time*4//3)

    possible_advances = []
    temp_rng = Xorshift(*rng.getState())
    temp_rng.getNextRandSequence(search_min)
    blink_rands = [int((r&0b1110)==0) for r in temp_rng.getNextRandSequence(search_max)]
    for advance in range(search_max-possible_length):
        blinks = blink_rands[advance:advance+possible_length]
        i = 0
        j = 0
        differences = []
        try:
            while i < reident_time:
                diff = 0
                while blink_bools[i] != blinks[j]:
                    diff += 1
                    j += 1
                if diff != 0:
                    differences.append(diff)
                j += 1
                i += 1
        except IndexError:
            continue
        pokemon_blink_count = sum(differences)
        possible_advances.append((pokemon_blink_count,advance))
    correct = min(possible_advances)
    rng.advances(search_min+sum(correct)+reident_time)
    adv = search_min+sum(correct)+reident_time
    print(f"found  at advances:{adv}")
    return rng

def recovByMunchlax(rawintervals:List[float])->Xorshift:
    """Recover the xorshift from the interval of Munchlax blinks.

    Args:
        rawintervals (List[float]): [description]

    Returns:
        Xorshift: [description]
    """
    advances = len(rawintervals)
    intervals = [interval+0.048 for interval in rawintervals]#Corrects for delays in observation results
    intervals = intervals[1:]#The first observation is noise, so we use the one after that.
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

def reidentify_by_pokeblink(rng:Xorshift, rawintervals:List[float], search_max=3*10**4, search_min=0, eps=0.1, dt = 0.01)->Tuple[Xorshift, float, float]:
    """Reidentify Xorshift state via intervals of Pokemon blinks 

    Args:
        rng (Xorshift): _description_
        rawintervals (List[float]): _description_
        search_max (_type_, optional): _description_. Defaults to 3*10**4.
        search_min (int, optional): _description_. Defaults to 0.
        eps (float, optional): _description_. Defaults to 0.1.
        dt (float, optional): _description_. Defaults to 0.01.
        blinktime (float, optional): _description_. Defaults to 0.285.

    Returns:
        Tuple[Xorshift, float, float]: reidentified Xorshift, next player blink timing, next pokemon blink timing
    """
    player_interval = 1.017
    blinktime = 0.285
    observed = rawintervals[1:]
    n = len(observed)

    #search
    search_range = search_max-search_min
    interval_rng = Xorshift(*rng.getState())
    interval_rng.advances(search_min)

    gen_range = search_range+int(sum(observed))+n+1
    true_intervals = [randrange(r,3,12)+blinktime for r in interval_rng.getNextRandSequence(gen_range)]

    starting = 0.0
    while starting < search_range:
        t = starting
        frag = True
        for i in range(n):
            true_idx = math.ceil(t/player_interval+i)
            diff = abs(observed[i]-true_intervals[true_idx])
            if diff>eps:
                frag = False
                break
            t += true_intervals[true_idx]

        if frag:
            next_pl_blink = math.ceil(t/player_interval)*player_interval -t 
            
            true_idx = math.ceil(t/player_interval+n)
            next_pk_blink = true_intervals[true_idx]

            found_idx = true_idx+search_min+1
            print(f"found at:{found_idx}")
            
            print(f"next player blink:{next_pl_blink}")
            print(f"next_pokemon blink:{next_pk_blink}")
            result_rng = Xorshift(*rng.getState())
            result_rng.advances(found_idx)
            return (result_rng, next_pl_blink, next_pk_blink)
        
        idx = math.ceil(starting/player_interval)
        diff = abs(observed[0]-true_intervals[idx])
        if diff>eps:
            starting += player_interval
        else:
            starting += dt
    
    return (None, None, None)

def reidentifyByMunchlax(rng:Xorshift, rawintervals:List[float], search_max=10**6, search_min=0, eps=0.1):
    """reidentify Xorshift state by intervals of observed blinks. 
    This method is faster than "reidentifyByBlinks" in most cases since it can be reidentified by less blinking.

    Args:
        rng (Xorshift): [description]
        rawintervals (List[int]): list of intervals of blinks. 7 or more are recommended.
        npc (int, optional): [description]. Defaults to 0.
        search_max ([type], optional): [description]. Defaults to 10**6.
        search_min (int, optional): [description]. Defaults to 0.

    Returns:
        Xorshift: [description]
    """
    intervals = rawintervals[1:]
    if search_max<search_min:
        search_min, search_max = search_max, search_min
    search_range = search_max - search_min

    prng = Xorshift(*rng.getState())
    prng.advances(search_min)
    blinkrands = [randrange(r,3,12)+0.285 for i,r in enumerate(prng.getNextRandSequence(search_range))]

    #search
    for idx in range(search_range):
        isSame = True
        for j in range(len(intervals)):
            e = blinkrands[idx+j]
            o = intervals[j]
            if abs(e-o)>eps:
                isSame=False
                break
        if isSame:
            print(f"found  at advances:{idx+len(intervals)+search_min}")
            result = Xorshift(*rng.getState())
            result.advances(idx+len(intervals)+search_min)
            return result