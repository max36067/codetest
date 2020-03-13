# codetest
## 問題
* **Docker系統並不熟悉**<br>
目前封裝的docker不一定完善，可能還會有些小bug

* **目前尚未實測有關分散式系統的相關問題**<br>
暫時以multiprocessing解決
想法: 網上有查詢到docker swarm的分散式結構方法，因初學docker，因此目前還未解決此問題

* **承上，有關異常檢測想法**<br>
想法: 藉由分散式系統生成task pool，讓manager發送task給worker，當worker有不可預期之狀況，會將task拋回task pool裡面<br>

* **改善過度快速擷取頁面問題**<br>
目前是使用time.sleep，日後若需改進可爬取免費IP網站存入IP pool，若IP被封鎖即至IP pool拿取新的IP<br>

### 更多詳細邏輯寫於程式碼內


## 安裝步驟

### 使用docker

```
$ docker pull mongo
$ docker pull max36067/ptt-scrapy
```

### 完成後創建網路

```
$ docker network create -d bridge ptt
```

### 依照順序開啟兩個container

```
$ docker run --name mymongo -v "/data:/data" -p 27017:27017 --network ptt  mongo
$ docker run --name pttscrapy  -p 1234:56 --network ptt -it codetest
```

開啟mongo的時候會遇到以下情況，請以**Crtl+C**退出即可
![image](https://imgur.com/cJfuadq.jpg)


實際擷取資料畫面<br>
![image](https://imgur.com/NSk6rop.jpg)


資料格式(以自身雲端資料庫為例，這樣比較好看xD)<br>
![image](https://imgur.com/RTjjfGB.jpg)
