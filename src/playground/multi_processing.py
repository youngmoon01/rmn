from multiprocessing import Process

def test(arg):
    print("Arg is " + arg)

if __name__ == '__main__':
    p1 = Process(target=test, args=["first"]) # args should be iterable(list, tuple etc)
    p2 = Process(target=test, args=["second"]) # args should be iterable(list, tuple etc)
    p3 = Process(target=test, args=["third"]) # args should be iterable(list, tuple etc)
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    print("process 1 completed")
    p2.join()
    print("process 2 completed")
    p3.join()
    print("process 3 completed")
