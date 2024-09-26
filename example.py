import time
from metrics_decorator.metrics_collection import metrics_collector, get_metrics

@metrics_collector
def test1():
    print("123")
    time.sleep(2)
    # raise Exception("xxx")
    print("234")

if __name__ == "__main__":
    test1()
    time.sleep(3)
    get_metrics("test1")
