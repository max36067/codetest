import queue
import multiprocessing as mp
from multiprocessing.managers import BaseManager
from ptt_scrapy import PTT


'''
模擬分散式系統架構，因目前無法將虛擬機及本地端連線，故先寫出此架構。
此為server端， 負責發送及接收任務
'''

task_queue =  queue.Queue()
result_queue = queue.Queue()

class QueueManager(BaseManager):
    pass
def return_task_queue():
    global task_queue
    return task_queue

def return_result_queue ():
    global result_queue
    return result_queue

def test():
    QueueManager.register('get_task_queue', callable=return_task_queue)
    QueueManager.register('get_result_queue', callable=return_result_queue)
    manager = QueueManager(address=('127.0.0.1', 5000), authkey=b'abc')
    manager.start()
    task = manager.get_task_queue()
    result = manager.get_result_queue()
    return task, result


if __name__=='__main__':
    ptt = PTT()
    task, result = test()
    for i in board_keys:
        n = mp.Process(target=ptt.date_check, args=(i, ))
        print('Put task %d...' % n)
        task.put(n)
        try:
            r = result.get(timeout=5)
        except queue.Empty:
            print('result queue is empty.')
    manager.shutdown()