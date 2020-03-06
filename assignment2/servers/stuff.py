import time
import threading
def test1Listner(test1Runnig,num,lis,dic):
    print(num)
    print(lis)
    print(dic)
    while(len(test1Runnig)==0):
        time.sleep(5)
        lis.append(1)
        
        
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