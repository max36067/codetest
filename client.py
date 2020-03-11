import time, sys, queue
from multiprocessing.managers import BaseManager
from ptt_scrapy import PTT


'''
此為客戶端，自manager端拿取任務後開始執行
'''


data_queue = queue.Queue()

class QueueManager(BaseManager):
    pass

def test():
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')
    server_addr = '此處輸入IP位置'
    print('Connect to server %s...' % server_addr)
    m = QueueManager(address=(server_addr, 5000), authkey=b'abc')
    m.connect()
    task = m.get_task_queue()
    result = m.get_result_queue()
    return task, result

if __name__ == "__main__":
    ptt = PTT()
    task, result = test()
    n = task.get(timeout=1)
    print('run task %d ...' % (n))
    time.sleep(1)
    result.put(r)
    print('task queue is empty.')
    print('worker exit.')