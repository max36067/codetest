import os
import pymongo

def open_db(board_title = None, start_date=None, end_date=None):
    '''
    打開 DataBase 此處使用MongoDB
    '''
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    client.server_info()
    db = client.ptt
    collect = db["pttscrapy"]
    try:
        finds = collect.find({'title': board_title, 'publishedTime':{'$gte':start_date, '$lte':end_date}})
        collect.create_index([('canonicalUrl'), pymongo.ASCENDING], unique=True)
    except:
        finds = None
    return collect, finds

def write_db(queue):
    '''
    寫入資料庫
    '''
    data = queue.get()
    collect, _ = open_db()
    try:
        collect.insert_one(data)
        print('資料寫入成功')
    except Exception as e:
        print(e)
        print('資料寫入失敗')
    print('=' * 30)
