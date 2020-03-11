import requests, threading, re, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import Database as db


class PTT:
    def __init__(self, queue=None):
        self.board_dict = {}
        self.cookie = {'over18':'1'}
        self.header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
        self.index_num = None
        self.board_title = None
        self.page = None
        self.queue = queue
        self.board_select()

    def board_select(self):
        '''
        取得所有熱門看板
        '''
        url = 'https://www.ptt.cc/bbs/hotboards.html'
        req = requests.get(url, headers = self.header).text
        res = BeautifulSoup(req, 'html.parser')
        board_html = res.find_all('a',{'class':'board'})
        board_name = res.find_all('div',{'class':'board-name'})
        board_name = [i.text for i in board_name]
        board_html = ['https://www.ptt.cc/' + i.get('href') for i in board_html]
        for num, name in enumerate(list(zip(board_name, board_html))):
            self.board_dict.update({num:name})
        print('熱門看板數量:', len(self.board_dict.keys()))

    def date_check(self, board_num):
        '''
        這裡主要是在做大概方向的日期抓取，可以抓出輸入時間的大概頁面範圍
        '''
        try:
            self.sd = datetime.strptime(self.start_date, '%Y-%m-%d')
            self.ed = datetime.strptime(self.end_date, '%Y-%m-%d') + timedelta(days=1)
            self.sd_timestamp =  int(self.sd.timestamp())
            self.ed_timestamp = int(self.ed.timestamp())
        except:
            print('請輸入正確的時間格式')
        if self.sd > self.ed:
            print('開始時間大於結束時間!')
            print('請重新輸入!')
            return
        url = self.board_dict[board_num][1]
        self.board_title = self.board_dict[board_num][0]
        if self.sd <= self.ed:
            print(f'現在正在 {self.board_title} 版')
            req = requests.get(url, headers = self.header, cookies = self.cookie).text
            bs = BeautifulSoup(req, 'html.parser')
            front_page = bs.find_all('a', {'btn wide'})
            for np in front_page:
                if '上頁' in np.text:
                # 當前頁碼
                    self.index_num = int(np.get('href').split('index')[-1].split('.')[0]) + 1
            back_ten = self.index_num
            # 擷取當頁所有文章日期
            page_now = f'https://www.ptt.cc/bbs/{self.board_title}/index{self.index_num}.html'
            _, page_now_date = self._take_date(page_now)
            date_in_now_page = max(page_now_date)
            count = 1
            while True:
                # 前推100頁，算出一天大概要往前爬多少頁
                if back_ten <= 100:
                    back_ten -= 10
                else:
                    back_ten -= 100

                front_ten_page = f'https://www.ptt.cc/bbs/{self.board_title}/index{back_ten}.html'
                _, page_ten_date_before = self._take_date(front_ten_page)
                date_in_ten_page_before = min(page_ten_date_before)
                '''計算前 10 頁約相隔多少天'''
                ten_page_date = date_in_now_page - date_in_ten_page_before
                if ten_page_date.days != 0:
                    self.a_day_page = 100 / ten_page_date.days
                    self.ed_page = int((date_in_now_page - self.ed).days * self.a_day_page) + 1
                    self.sd_page = int((date_in_now_page - self.sd).days * self.a_day_page) + 1
                    print(f'現在與指定結束日期相隔約{self.ed_page}頁')
                    print(f'現在與指定開始日期相隔約{self.sd_page}頁')
                    # 先嘗試取得結束日期頁數上的日期
                    self._date_tuning()
                    break
                else:
                    continue

    def _date_tuning(self):
        '''
        主要在做頁面微調，精準抓出頁面區間
        '''
        ed_item_page = self.index_num - self.ed_page
        sd_item_page = self.index_num - self.sd_page
        # 往前後調整頁數
        print('調整正確頁數中...')
        while True:
            ed_url = f'https://www.ptt.cc/bbs/{self.board_title}/index{ed_item_page}.html'
            sd_url = f'https://www.ptt.cc/bbs/{self.board_title}/index{sd_item_page}.html'
            _, ed_check_date = self._take_date(ed_url)
            _, sd_check_date = self._take_date(sd_url)

            # 細部調整日期
            if min(sd_check_date) <= self.sd <= max(sd_check_date) and min(ed_check_date) <= self.ed <= max(ed_check_date):
                break
            if self.sd <= min(sd_check_date):
                sd_item_page -= 1
            elif self.sd >= max(sd_check_date):
                sd_item_page += 1

            if self.ed <= min(ed_check_date):
                ed_item_page -= 1
            elif self.ed >= max(ed_check_date):
                ed_item_page += 1
            time.sleep(1)


        print('開始頁面:', sd_item_page)
        print('結束頁面:', ed_item_page)
        print(f'看板{self.board_title}內文開始抓取....')
        self._take_item(sd_item_page, ed_item_page)

    def _take_item(self, sd_item_page, ed_item_page):
        '''
        擷取區間內所有資料
        '''
        for i in range(sd_item_page, ed_item_page + 1):
            url = f'https://www.ptt.cc/bbs/{self.board_title}/index{i}.html'
            href, date = self._take_date(url)
            _, finds= db.open_db(self.board_title, start_date = self.sd_timestamp, end_date = self.ed_timestamp)
            if finds != None:
                db_urls = [find['canonicalUrl'] for find in finds]
            else:
                db_urls = []
            for l in range(len(date)):
                item_dict = {}
                if not href[l] in db_urls:
                    if self.sd < date[l] < self.ed:
                        '''
                        疑問一:
                        若以網址判斷是否需要進去擷取文章內容，並且保持raw data，
                        資料更新時間是否就無存在的必要?
                        若誤會題目請見諒
                        '''
                        publishedTime = date[l].timestamp()
                        createdTime = datetime.today()
                        autherId, autherName, title, content, push_list = self._item_scrapy(href[l])
                        item_dict.update({'board':self.board_title,'autherId':autherId, 'autherName':autherName, 'title':title, 'publishedTime':publishedTime, 'content':content, 'canonicalUrl': href[l],'creatTime':createdTime,'comment':push_list})
                        print('文章擷取完成!')
                        # print(title)
                        self.queue.put(item_dict)
                        db.write_db(self.queue)
                        time.sleep(2)
                else:
                    print('此資料已經存在!')

    def _item_scrapy(self, url):
        push_list = []
        commentContents = []
        cTs = []
        ftp = requests.get(url, headers = self.header, cookies = self.cookie).text
        ftp_bs = BeautifulSoup(ftp, 'html.parser')
        '''抓出作者及標題'''
        detail_of_item = ftp_bs.find('div', {'id' : 'main-content'})
        auther = detail_of_item.find_all('span', {'class': 'article-meta-value'})
        autherId = auther[0].text.split(' ')[0]
        autherName = re.sub('[()]', '', auther[0].text.split(' ')[1])
        title = auther[2].text

        '''把所有干擾擷取內文的部分抽取出來'''
        ms = detail_of_item.find_all('div', {'class': 'article-metaline'})
        for m in ms:
            m.extract()
        ms = detail_of_item.find_all('div', {'class': 'article-metaline-right'})
        for m in ms:
            m.extract()

        '''推文者Id及內容'''
        commentId = detail_of_item.find_all('span', {'class':'f3 hl push-userid'})
        commentcontent = detail_of_item.find_all('span', {'class':'f3 push-content'})
        ipdatetime = detail_of_item.find_all('span', {'class':'push-ipdatetime'})
        for com in commentId:
            push_list.append({'commentId':com.text})

        for con in commentcontent:
            push_content = con.text.replace(':', '')
            commentContents.append(push_content)

        '''
        疑問二:
        推文時間沒有推文年份
        無法轉為時間戳格式
        '''
        for ip in ipdatetime:
            commentTime = ip.text.split('\n')[0].lstrip().split(' ')
            if len(commentTime[0]) > 5 and len(commentTime) < 3:
                commentTimes = commentTime[-1]
            elif len(commentTime) >= 3:
                commentTimes = ' '.join(commentTime[-2:])
            else:
                commentTimes = ' '.join(commentTime)
            cTs.append(commentTimes)
        for l in range(len(push_list)):
            push_list[l].update({'commentContent':commentContents[l], 'commentTime':cTs[l]})

        '''最後抽取推文及更新'''
        push = detail_of_item.find_all('div', {'class':'push'})
        update_item = detail_of_item.find_all('span', {'class':'f2'})
        for p in push:
            p.extract()
        for u in update_item:
            u.extract()
        push = detail_of_item.find_all('div', {'class':'push'})
        content = detail_of_item.text.replace('\n', '')
        return autherId, autherName, title, content, push_list

    def _take_date(self, url):
        ftp = requests.get(url, headers = self.header, cookies=self.cookie).text
        ftp_bs = BeautifulSoup(ftp, 'html.parser')
        r_list_sep = ftp_bs.find('div', class_ = 'r-list-sep')
        '''判斷是否有置頂文章'''
        if r_list_sep == None:
            item = ftp_bs.find_all('div', {'class':"r-ent"})
        else:
            item = r_list_sep.find_previous_siblings('div', class_ = 'r-ent')
        date_in_the_page = []
        item_hrefs = []
        titles = []
        utc_8 = timedelta(hours=8)
        for i in item:
            item_href = i.find('div', {'class':'title'}).find('a')
            if item_href != None:
                item_href = item_href.get('href')
                date_time = item_href.split('.')[1]
                dt = datetime.utcfromtimestamp(int(date_time))
                date_in_the_page.append(dt + utc_8)
                item_hrefs.append('https://www.ptt.cc' + item_href)
        return item_hrefs, date_in_the_page

    def run(self, start_date, end_date):
        # 利用 multiprocessing一次爬取多個看板
        self.start_date = start_date
        self.end_date = end_date
        pool = mp.Pool(processes=4)
        for i in range(len(self.board_dict.keys())):
            pool.apply_async(self.date_check, args=(i,))
        pool.close()
        pool.join()
        # self.date_check(20)


if __name__ == '__main__':
    import multiprocessing as mp
    queue = mp.Manager().Queue()
    ptt = PTT(queue)
    start_date = input('請輸入開始年月日(YYYY-MM-DD):')
    end_date = input('請輸入結束年月日(YYYY-MM-DD):')
    ptt.run(start_date, end_date)