from xorshift import Xorshift
import secrets
import time
import calc

def splitstate(state:int):
    result = []
    for i in range(4):
        result.append(state&0xFFFFFFFF)
        state>>=32
    return result[::-1]


def main():
    prng = Xorshift(0x12,0x34,0x56,0x00)
    for i in range(10):
        print(*list(map(hex,prng.getState())))
        prng.prev()

if __name__ == "__main__":
    main()