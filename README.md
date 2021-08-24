# 爬取虛擬貨幣

藉由airflow來設定每十分鐘爬取一次資料，

![image](https://github.com/zaqxsw800402/coincap_dash/blob/main/picture/airflow.png?raw=true)

經pandas來清理資料，並存入postgresql

由dash及plotly來展現蒐集到的資料

可藉由選單來挑選想要看的貨幣

![image](https://github.com/zaqxsw800402/coincap_dash/blob/main/picture/dash.png?raw=true)

最底下有設置該硬幣低於多少元會寄信通知