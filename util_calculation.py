import numpy as np
from collections import deque

class UTILCalculation:
    def __init__ (self, relations):
        self.RELATIONS = deque(relations)
    
    def projection(self, cube):
        return np.max(cube, axis=0)

    def join(self, r1,r2):
        return r1[:,:, None] + r2[:, None, :]


    def hypercube(self, R):
        proj = None
        if len(R) < 2:
            return np.asarray(R)

        try:
            # get first relation
            r1 = R.pop()
            # get second relation
            r2 = R.pop()

            proj = self.projection(self.join(r1,r2))

            R.append(proj)
            proj = self.hyperCube(R)
        except IndexError as index:
            print(index)

        return np.asarray(proj)