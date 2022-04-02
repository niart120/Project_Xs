from xorshift import Xorshift

def main():
    print("input xorshift state (state[0] state[1])")
    state = [int(x,0) for x in input().split()]
    mask = 0xFFFFFFFF
    state = [state[0]>>32,state[0]&mask,state[1]>>32,state[1]&mask]

    rng = Xorshift(*state)
    rng.advances(12921)
    print(generate(rng))


def generate(rng:Xorshift):
    pokerng = Xorshift(*rng.getState())
    count = 0
    getrand = lambda :(pokerng.next()%0xFFFFFFFF+0x80000000)&0xFFFFFFFF
    ec = getrand()
    tidsid = getrand()
    pid = getrand()

    count += 2
    #fixedIVs
    ivs = [-1]*6
    i = 0

    ivCount = 3
    while i < ivCount:
        stat = rng.range(0,6)
        count += 1
        if ivs[stat] == -1:
            ivs[stat] = 31
            i += 1

    #unfixedIVs
    for i in range(6):
        if ivs[i] == -1:
            ivs[i] = rng.range(0,32)
            count += 1
    
    ability = getrand()%2
    count += 1
    gender = None
    #gender = getrand()%255
    #count += 1

    nature = getrand()%25
    count += 1

    height = getrand()%128+ getrand()%129
    weight = getrand()%128+ getrand()%129
    count += 4

    print(f"advance:{count}")

    return (ec,tidsid,pid,ivs,ability,gender,nature,height,weight)

if __name__ == "__main__":
    main()