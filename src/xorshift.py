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

    def advances(self,length:int):
        self.getNextRandSequence(length)

    def range(self,mi:int,ma:int)->int:
        """generate random integer value in [mi,ma)

        Args:
            mi ([int]): minimum
            ma ([int]): maximam

        Returns:
            [int]: random integer value
        """
        return self.next() % (ma-mi) + min

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