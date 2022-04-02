from typing import Tuple
from bisect import bisect_left
import random

def main():
    #state = (0x01234567, 0x89abcdef, 0xdeadbeef, 0x00c0ffee)
    #state = (0x65bd81ba, 0x835c5170, 0x865ecefc, 0x425552da)
    state = (0xd53b1d85, 0xa191c9c1, 0x98c891c1, 0x88ee0339)
    rng = Xorshift(*state)
    rng.advance(0)
    ds = Digsite()

    for i in range(50):
        result = ds.generate(rng.getState(), 0)
        print(f"idx:{i+50}, {result}")
        print(rng.rangefloat(0,1030)/5.0)

class Digsite(object):
    def __init__(self):
        self.item_name = ["Red Sphere S", "Blue Sphere S", "Green Sphere S", "Prism Sphere S", "Pale Sphere S", "Red Sphere L", "Blue Sphere L", "Green Sphere L", "Prism Sphere L", "Pale Sphere L", "Revive", "Max Revive", "Red Shard", "Blue Shard", "Yellow Shard", "Green Shard", "Sun Stone", "Moon Stone", "Fire Stone", "Thunder Stone", "Water Stone", "Leaf Stone", "Oval Stone", "Everstone", "Odd Keystone", "Star Piece", "Heart Scale", "Root Fossil", "Claw Fossil", "Helix Fossil", "Dome Fossil", "Old Amber", "Armor Fossil", "Skull Fossil", "Rare Bone", "Light Clay", "Iron Ball", "Icy Rock", "Smooth Rock", "Heat Rock", "Damp Rock", "Mysterious Shard S", "Mysterious Shard L", "Hard Stone", "Flame Plate", "Splash Plate", "Zap Plate", "Meadow Plate", "Icicle Plate", "Fist Plate", "Toxic Plate", "Earth Plate", "Sky Plate", "Mind Plate", "Insect Plate", "Stone Plate", "Spooky Plate", "Draco Plate", "Dread Plate", "Iron Plate", "Pixie Plate"]
        weight_BD = [122,150,106,27,20,61,75,53,13,10,10,2,12,25,22,12,15,3,30,30,5,5,0,20,4,10,30,4,12,12,1,4,0,12,10,5,2,11,5,11,5,30,10,20,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        weight_SP = [150,122,106,20,27,75,61,53,10,13,10,2,22,15,12,22,3,15,5,5,30,30,0,20,4,10,30,12,4,4,13,4,12,0,10,2,5,5,11,5,11,30,10,20,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        
        base_bd = 0
        base_sp = 0
        cum_weight_BD = []
        cum_weight_SP = []

        for i in range(61):
            base_bd += weight_BD[i]
            base_sp += weight_SP[i]
            cum_weight_BD.append(base_bd)
            cum_weight_SP.append(base_sp)
        
        self.cumulative_weight = [cum_weight_BD,cum_weight_SP]
        self.sum_weight = [sum(weight_BD),sum(weight_SP)]

        
    def generate(self, rngstate:Tuple[int,int,int,int], version:int):
        rng = Xorshift(*rngstate)

        cumweight = self.cumulative_weight[version]
        sumw = self.sum_weight[version]
        
        """
        # number of items
        _ = rng.range(2,5)

        # is Box generated?
        is_box_gen = rng.next()
        
        #(if Box is generated)
        #if is_box_gen%2==0:
        if True:
            #print("box gen:True")
            # Box rareliity
            _ = rng.next()
            # Box type
            _ = rng.next()

            # Box position
            _ = rng.next()
            _ = rng.next()
        else:
            #print("box gen:False")
            pass
        """
        # item type
        r = rng.range(0,sumw)
        idx = bisect_left(cumweight,r)
        item = self.item_name[idx]

        # item position
        px = rng.range(0,12)
        py = rng.range(0,9)
        return (item, px, py)

class Xorshift(object):
    def __init__(self,s0,s1,s2,s3):
        self.x = s0
        self.y = s1
        self.z = s2
        self.w = s3

    def next(self):
        s0 = self.x
        s1 = self.y
        s2 = self.z
        s3 = self.w

        t = s0 ^ s0 << 11 & 0xFFFFFFFF
        self.x = s1
        self.y = s2
        self.z = s3
        self.w = t ^ t >> 8 ^ s3 ^ s3 >> 19

        return self.w

    def prev(self):
        s0 = self.x
        s1 = self.y
        s2 = self.z
        s3 = self.w

        t = s2 >> 19 ^ s2 ^ s3
        t ^= t >> 8
        t ^= t >> 16
        
        t ^= t << 11 & 0xFFFFFFFF
        t ^= t << 22 & 0xFFFFFFFF

        self.x = t
        self.y = s0
        self.z = s1
        self.w = s2

        return self.w

    def advance(self,length:int):
        self.getNextRandSequence(length)

    def range(self,mi:int,ma:int)->int:
        """generate random integer value in [mi,ma)

        Args:
            mi ([int]): minimum
            ma ([int]): maximam

        Returns:
            [int]: random integer value
        """
        return self.next() % (ma-mi) + mi

    def value(self)->float:
        """generate random value in [0,1]

        Returns:
            float: random value
        """
        return (self.next() & 0x7fffff) / 8388607.0

    def rangefloat(self,mi:float,ma:float)->float:
        """generate random value in [mi,ma]

        Args:
            mi (float): minimum
            ma (float): maximam

        Returns:
            [type]: [description]
        """
        t = self.value()
        return t * mi + (1-t) * ma

    def getNextRandSequence(self,length):
        return [self.next() for _ in range(length)]

    def getPrevRandSequence(self,length):
        return [self.prev() for _ in range(length)]

    def getState(self):
        return [self.x, self.y, self.z, self.w]

    def setState(self, s0, s1, s2, s3):
        self.x = s0
        self.y = s1
        self.z = s2
        self.w = s3

if __name__ == "__main__":
    main()