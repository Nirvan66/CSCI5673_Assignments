import time
import threading
def test1Listner():
    while(test1Runnig):
        time.sleep(2)
        lis.append(1)
        print(num)
        print(lis)
        print(dic)
        
        
if __name__=="__main__":
    num = 1
    lis = [1,2,3]
    dic = {1:'1',2:'2'}
    test1Runnig = True
    test1Thread = threading.Thread(target=test1Listner, name='test1')
    test1Thread.daemon = True
    test1Thread.start()
    while(test1Runnig):
        inp = input("'1' to end thread:")
        if inp=='1':
            test1Runnig = False
    test1Thread.join()