import numpy as np
from collections import deque
import time


R_A3_A2 = np.array([[1, np.NINF, np.NINF],
                [np.NINF, 2, np.NINF], 
                [np.NINF,np.NINF,5]])
R_A3_A1 = np.array([[3, np.NINF, np.NINF], 
                [np.NINF, 4, np.NINF], 
                [np.NINF, np.NINF, 6]])

R_A3_A4 = np.array([[8, np.NINF, np.NINF], 
                [np.NINF, 7, np.NINF], 
                [np.NINF, np.NINF, 9]])


R4 = np.array([
    [11, np.NINF, np.NINF],
    [np.NINF, 21, np.NINF],
    [np.NINF, np.NINF, 4]
])


r1 = np.array([
    [26, np.NINF, np.NINF],
    [np.NINF, 65, np.NINF],
    [np.NINF, np.NINF, 117]])

r2 = np.array([
    [49, np.NINF, np.NINF],
    [np.NINF, 35, np.NINF],
    [np.NINF, np.NINF, 28]])


Relations = deque()


def populate():
    Relations.append(r1)
    Relations.append(r2)
    # Relations.append(R_A3_A2)
    # Relations.append(R_A3_A1)
    # Relations.append(R_A3_A4)

def projection(cube):
    return np.max(cube, axis=0)

def join(r1,r2):
    return r1[:,:, None] + r2[:, None, :]

def hyperCube(R):
    if len(R) < 2:
        return np.asarray(R)

    try:
        # get first relation
        r1 = R.pop()
        # get second relation
        r2 = R.pop()

        proj = projection(join(r1,r2))

        R.append(proj)
        proj = hyperCube(R)
    except IndexError as index:
        print(index)

    return np.asarray(proj)



start_time = time.time()


populate()
cube = hyperCube(Relations)
# print("Hypercube R_A3_A2, R_A3_A1, R_A3_A4\n", cube)
print(cube)
print("--- %s seconds ---" % (time.time() - start_time))






