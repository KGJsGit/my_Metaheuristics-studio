import math
import numpy as np
import random
import timeit
from threading import Thread
import functools

dist_ar = []  # 거리표(global)
# limit_time = 36 # 제한시간(global)
cities_count = 0  # 도시 수(global)
dots_list = []  # 도시 리스트(global)

# Hyper Parameter
limits = (60) * 36/60  # 제한시간
nestCOUNT = 10 # 해집단 내 둥지 갯수

# 시간제한 데코레이터
def timeout(seconds_before_timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, seconds_before_timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(seconds_before_timeout)
            except Exception as e:
                print('error starting thread')
                raise e
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco


# 거리표 제작(param : 문제 경로) : dist_df
def make_distArray(str):
    global dist_ar
    global limit_time
    global cities_count
    global dots_list

    reader = open(str, mode='rt', encoding='utf-8')
    dots_list = reader.read().split("\n")  # ['x1 y1', 'x2 y2', 'x3 y3' ... 'xn yn']
    cities_count = int(dots_list.pop(0))
    limit_time = float(dots_list.pop())

    x_list = []  # ['x1', 'x2', 'x3' ... 'xn']
    y_list = []  # ['y1', 'y2', 'y3' ... 'yn']
    for i in range(cities_count):
        temp = dots_list[i].split(" ")
        x_list.append(float(temp[0]))
        y_list.append(float(temp[1]))

    dist_ar = []
    for n in range(cities_count):
        temp = []
        for m in range(cities_count):
            temp.append(round((math.sqrt(((x_list[m] - x_list[n]) ** 2) + ((y_list[m] - y_list[n]) ** 2))), 2))
        dist_ar.append(temp)

    dist_ar = np.array(dist_ar)
    print(dist_ar)

# 거리표를 이용한 적합도 매칭 함수
def cal_fit(stri):
    fit = 0
    for steps in range(len(stri) - 1):
        fit += dist_ar[stri[steps], stri[steps + 1]]
    return fit

def levyFlight(u) :
    # u의 세제곱근분의 1
    return math.pow(u,-1.0/3.0)

def randF() :
    return random.uniform(0.0001,0.9999)

def levySwap(route, i, j) :
    temp = route[i]
    route[i] = route[j]
    route[j] = temp
    return route

def levyTwoOpt(nest, a, c) :
    nest = nest[:]
    new_nest = levySwap(nest, a, c)
    return new_nest

def levyDoublebridge(nest, a, b, c, d) :
    nest = nest[:]
    new_nest = levySwap(nest, a, b)
    new_nest = levySwap(new_nest, b, d) # ??
    return new_nest

def CS() :
    generation = 0  # 현재 세대
    egg = []  # temp chromosome
    egg_fit = []  # temp fitness
    pa = int(0.2 * nestCOUNT) # a fraction of worse nests

    # Initialize
    for i in range(nestCOUNT):
        egg.append(random.sample(range(0, cities_count), cities_count))

    for i in range(nestCOUNT):
        egg_fit.append(round(cal_fit(egg[i]), 5))

    populations = np.array([egg, egg_fit])
    populations = populations.T
    print('초기화 최대 해 : \n', populations[0, 0], "\n", populations[0, 1])

    while 1:
        generation += 1
        populations = populations[np.argsort(populations[:, 1])]

        # Get a cuckoo randomly by levy flight
        cuckooNest = populations[random.randint(0, nestCOUNT-1), 0]
        if(levyFlight(randF())>2) :
            cuckooNest = levyDoublebridge(cuckooNest, random.randint(0,cities_count-1), random.randint(0,cities_count-1)
                                          , random.randint(0,cities_count-1), random.randint(0,cities_count-1))
        else :
            cuckooNest = levyTwoOpt(cuckooNest, random.randint(0,cities_count-1), random.randint(0,cities_count-1))
        randomNestIndex = random.randint(0, nestCOUNT-1)

        # Evaluate and replace
        if(populations[randomNestIndex, 1] > cal_fit(cuckooNest)) :
            populations[randomNestIndex, 0] = cuckooNest
            populations[randomNestIndex, 1] = cal_fit(cuckooNest)

        # Pa of worse nests are abandoned and new ones built
        for i in range(nestCOUNT-pa, nestCOUNT) :
            populations[i, 0] = random.sample(range(0, cities_count), cities_count)
            populations[i, 1] = cal_fit(populations[i,0])
        populations = populations[np.argsort(populations[:, 1])]
        print(generation, '세대 최적 해 : \n', populations[0, 0], "\n", populations[0, 1])


@timeout(limits)
def start_CS(stri) :
    make_distArray(stri)
    CS()

try :
    start = timeit.default_timer()
    start_CS("2opt_dots/2opt_cycle100.in")
    stop = timeit.default_timer()
    print(stop - start)
except :
    stop = timeit.default_timer()
    print(stop - start)

'''
//질문
1. Pc는 뭐고 왜 줬을까?
2. 왜 버리지 않고 twoopt를 줬을까?? -> 준게 더 좋긴하넹?
3. doublebridge 알고리즘이 이해가 잘안가네???


//비교
numGA : numpy GA
numCS : numpy CS
시간제한 : 36s
타겟 : 2opt_cycle100.in

numGA : generation / fitness (chromosome수 : 10)
    3287/1990
    3272/2107
    3290/2299
    3310/2253
    3298/1967
    
numGA : generation / fitness (chromosome수 : 50)
    1137/1847
    1143/1707
    1133/2006
    1141/1823
    1141/2022

numCS : generation / fitness (nest 수 : 10)
    55677/1655
    57063/1589
    53056/1678
    52588/1757
    53212/1869
    
numCS : generation / fitness (nest 수 : 20)
    67396/1741
    69157/1744
    71023/1782
    70852/1830
    70993/1722
    
numCS : generation / fitness (nest 수 : 50)
    32880/2361
    32861/2373
    32744/2308
    32523/2281
    32267/2417
    
enhanced numCS : generation / fitness (nest 수 : 10)
    151389/1470
    152319/1609
    164071/1579
    181645/1418
    182080/1594
'''
