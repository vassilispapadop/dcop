import numpy as np
TIME_SLOTS = 3
R_A3_A2 = np.array([[100, 0, 0],
                [0, 200, 0], 
                [0,0,500]])
R_A3_A1 = np.array([[200, 0, 0], 
                [0, 500, 0], 
                [0,0, 100]])

def createHypercube(A,B):
    cube = []
    for i in range(0, TIME_SLOTS):
        r = A[i][:, None] + B[i][None, :]
        cube.append(r)

    return np.asarray(cube)

def createProjection(cube):
    return np.max(cube, axis=0)

cube = createHypercube(R_A3_A2, R_A3_A1)
print("Hypercube R_A3_A2, R_A3_A1\n", cube)

projection = createProjection(cube)
print("Projection A3_M1\n", projection)






