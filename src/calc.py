import numpy as np
from functools import reduce
from bisect import bisect

def getZero(size=32):
    return np.zeros((size,size),dtype="uint8")

def getI(size=32):
    return np.identity(size,dtype="uint8")

def getShift(n,size=32):
    return np.eye(size,k=n,dtype="uint8")

def getTrans():
    t11,t12,t13,t14 = getZero(),getI(),getZero(),getZero()
    t21,t22,t23,t24 = getZero(),getZero(),getI(),getZero()
    t31,t32,t33,t34 = getZero(),getZero(),getZero(),getI()
    t41,t42,t43,t44 = (getI()^getShift(-8))@(getI()^getShift(11))%2,getZero(),getZero(),getI()^getShift(-19)

    
    trans = np.block([
        [t11,t12,t13,t14],
        [t21,t22,t23,t24],
        [t31,t32,t33,t34],
        [t41,t42,t43,t44],
        ])

    return trans

def getS(intervals,rows = 39):
    intervals = intervals[:rows]
    t = getTrans()
    t_ = getTrans()

    s = np.zeros((4*rows,128),"uint8")
    for i in range(rows):
        s[4*i:4*(i+1)] = t[-4:]
        for j in range(intervals[i]):
            t = t@t_%2
    return s

def getS_munchlax(intervals):
    intervals = intervals[::-1]
    section = [0, 3.4333333333333336, 3.795832327504833, 3.995832327504833, 4.358332394560066, 4.558332394560066, 4.9208324616153, 5.120832461615299, 5.483332528670533, 5.683332528670532, 6.045832595725767, 6.2458325957257665, 6.608332662781, 6.808332662780999, 7.170832729836233, 7.370832729836232, 7.733332796891467, 7.933332796891467, 8.2958328639467, 8.4958328639467, 8.858332931001934, 9.058332931001933, 9.420832998057167, 9.620832998057166, 9.9833330651124, 10.1833330651124, 10.545833132167635, 10.745833132167634, 11.108333199222866, 11.308333199222865, 11.6708332662781, 11.8708332662781, 12.233333333333334,]
    t = getTrans()
    t_ = getTrans()

    s = np.zeros((128,128),"uint8")
    safe_intervals = []
    for i in range(32):
        #intervals[-1]を挿入した際のインデックスが奇数だと危険な値の可能性がある
        is_carriable = bisect(section,intervals[-1])%2==1

        while is_carriable:
            #スキップする
            t = t@t_%2
            #危険な値を除外
            intervals.pop()
            is_carriable = bisect(section,intervals[-1])%2==1
        s[4*i:4*(i+1)] = t[105:109]
        t = t@t_%2
        safe_intervals.append(intervals.pop())
    return s, safe_intervals

def gauss_jordan(mat,observed:list):
    r,c = mat.shape

    bitmat = [list2bitvec(mat[i]) for i in range(r)]

    res = [d for d in observed]
    #forward elimination
    pivot = 0
    for i in range(c):
        isfound = False
        for j in range(i,r):
            if isfound:
                check = 1<<(c-i-1)
                if bitmat[j]&check==check:
                    bitmat[j] ^= bitmat[pivot]
                    res[j] ^= res[pivot]
            else:
                check = 1<<(c-i-1)
                if bitmat[j]&check==check:
                    isfound = True
                    bitmat[j],bitmat[pivot] = bitmat[pivot],bitmat[j]
                    res[j],res[pivot] = res[pivot],res[j]
        if isfound:
            pivot += 1
    for i in range(c):
        check = 1<<(c-i-1)
        assert bitmat[i]&check>0
    
    #backward assignment
    for i in range(1,c)[::-1]:
        check = 1<<(c-i-1)
        for j in range(i)[::-1]:
            if bitmat[j]&check==check:
                bitmat[j] ^= bitmat[i]
                res[j] ^= res[i]
    return res[:c]

def getInverse(mat):
    r,c = mat.shape
    assert r==c
    n = r

    res = [(1<<i) for i in range(n)]
    res = res[::-1]#identity matrix

    bitmat = [list2bitvec(mat[i]) for i in range(n)]

    pivot = 0
    for i in range(n):
        isfound = False
        for j in range(i,n):
            if isfound:
                check = 1<<(n-i-1)
                if bitmat[j]&check==check:
                    bitmat[j] ^= bitmat[pivot]
                    res[j] ^= res[pivot]
            else:
                check = 1<<(n-i-1)
                if bitmat[j]&check==check:
                    isfound = True
                    bitmat[j],bitmat[pivot] = bitmat[pivot],bitmat[j]
                    res[j],res[pivot] = res[pivot],res[j]
        if isfound:
            pivot += 1
    
    #backward assignment
    for i in range(1,n)[::-1]:
        check = 1<<(n-i-1)
        for j in range(i)[::-1]:
            if bitmat[j]&check==check:
                bitmat[j] ^= bitmat[i]
                res[j] ^= res[i]
    return res

def bitvec2list(bitvec,size=128):
    lst = [(bitvec>>i)%2 for i in range(size)]
    return np.array(lst[::-1])

def list2bitvec(lst):
    bitvec = reduce(lambda p,q: (int(p)<<1)|int(q),lst)
    return bitvec
    
def reverseStates(rawblinks:list, intervals:list)->int:
    blinks = []
    for b in rawblinks:
        blinks.extend([0,0,0])
        blinks.append(b)

    #print(blinks)
    s = getS(intervals)
    lst_result = gauss_jordan(s, blinks)
    bitvec_result = list2bitvec(lst_result)

    result = []
    for i in range(4):
        result.append(bitvec_result&0xFFFFFFFF)
        bitvec_result>>=32
    
    result = result[::-1]#reverse order
    return result

def reverseFloatRange(f:float,mi:float,ma:float):
    norm_f = (ma-f)/(ma-mi)
    norm_i = int(norm_f*8388607.0)
    return int(norm_f*8388607.0)&0x7fffff

def reverseStatesByMunchlax(intervals:list)->int:
    s, safe_intervals = getS_munchlax(intervals)
    bitvectorized_intervals = [reverseFloatRange(30.0*f,100,370)>>19 for f in safe_intervals]
    bitlst_intervals = []
    for b in bitvectorized_intervals[::-1]:
        for i in range(4):
            bitlst_intervals.append(b&1)
            b >>= 1
    bitlst_intervals = bitlst_intervals[::-1]

    bitvec_result = list2bitvec(gauss_jordan(s, bitlst_intervals))
    result = []
    for i in range(4):
        result.append(bitvec_result&0xFFFFFFFF)
        bitvec_result>>=32
    
    result = result[::-1]#reverse order
    return result