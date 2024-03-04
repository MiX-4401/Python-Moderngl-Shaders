import time as t
a = [x for x in range(10)]
num: int = 0
while True:
    num += 60
    print(num // 60, a[num // 60])
    t.sleep(1)