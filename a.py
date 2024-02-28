
kernalX: list = [
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
] 
kernalY: list = [
    [-1, 2, 1],
    [0, 0, 0],
    [-1, 2, 1],
]

resolution: tuple = (100, 100)
fragcoord:  tuple = (0.5, 0.6)
i, j = (-1, -1)
for i in [-1, 0, 1]:
    for j in [-1, 0, 1]:
        
        x: float = (fragcoord[0] + float(i)) / resolution[0]
        y: float = (fragcoord[1] + float(j)) / resolution[1]
        
        print((i,j), fragcoord, (x, y))

    #     j += 1
    # i += 1

