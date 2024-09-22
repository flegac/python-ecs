import math

from easy_kit.timing import TimingTestCase, time_func


def update1(a, b):
    return math.cos(a) + math.sin(b)


def update2(a, b):
    return math.sin(a) + math.cos(b)



def update3(a, b):
    return math.cos(a) - math.sin(b)


def update4(a, b):
    return math.sin(a) - math.cos(b)


DATA_SIZE = 1_000_000
STEPS = 100


class TestIt(TimingTestCase):

    @time_func
    def test_00(self):
        data = [0 for _ in range(2 * DATA_SIZE)]

        for _ in range(STEPS):
            for i in range(0, 2 * DATA_SIZE, 2):
                data[i] = update1(data[i], data[i + 1])

            for i in range(0, 2 * DATA_SIZE, 2):
                data[i + 1] = update2(data[i], data[i + 1])

            # for i in range(0, 2 * DATA_SIZE, 2):
            #     data[i ] = update3(data[i], data[i + 1])
            #
            # for i in range(0, 2 * DATA_SIZE, 2):
            #     data[i + 1] = update4(data[i], data[i + 1])
        print(sum(data))

    @time_func
    def test_01(self):
        data = [0 for _ in range(2 * DATA_SIZE)]

        for _ in range(STEPS):
            for i in range(0, 2 * DATA_SIZE, 2):
                data[i] = update1(data[i], data[i + 1])
                data[i + 1] = update2(data[i], data[i + 1])
                # data[i] = update3(data[i], data[i + 1])
                # data[i + 1] = update4(data[i], data[i + 1])
        print(sum(data))

    @time_func
    def test_10(self):
        data = [0 for _ in range(DATA_SIZE)]
        data2 = [0 for _ in range(DATA_SIZE)]

        for _ in range(STEPS):
            for i in range(DATA_SIZE):
                data[i] = update1(data[i], data2[i])
            for i in range(DATA_SIZE):
                data2[i] = update2(data[i], data2[i])
            # for i in range(DATA_SIZE):
            #     data[i] = update3(data[i], data2[i])
            # for i in range(DATA_SIZE):
            #     data2[i] = update4(data[i], data2[i])

        print(sum(data) + sum(data2))

    @time_func
    def test_11(self):
        data = [0 for _ in range(DATA_SIZE)]
        data2 = [0 for _ in range(DATA_SIZE)]

        for _ in range(STEPS):
            for i in range(DATA_SIZE):
                data[i] = update1(data[i], data2[i])
                data2[i] = update2(data[i], data2[i])
                # data[i] = update3(data[i], data2[i])
                # data2[i] = update4(data[i], data2[i])

        print(sum(data) + sum(data2))
