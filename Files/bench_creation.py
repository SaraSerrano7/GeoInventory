import time


def sort_seven():
    """Sort a list of seven items"""
    for _ in range(100_000):
        sorted([3,2,4,5,1,5,3])
    # time.sleep(5)
    test_2()

def test_2():
    for _ in range(100_000):
        sorted([3,2,4,5,1,5,3,6,8,21,9])

def sort_three():
    """Sort a list of three items"""
    for _ in range(100_000):
        sorted([3,2,4])
    # time.sleep(1)

__benchmarks__ = [
    (sort_seven, sort_three, "Sorting 3 items instead of 7"),
    (sort_three, sort_seven, "Sorting 7 items instead of 3"),
]

if __name__ == '__main__':
    print("Benchmarks:", __benchmarks__)