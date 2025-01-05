import requests
from bs4 import BeautifulSoup
import mysql.connector
from config import DB_CONFIG
import json
from datetime import datetime, timedelta
import time
import schedule
import time

def connect_to_database():
    """连接到数据库"""
    try:
        # 使用配置文件中的数据库信息连接
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("成功连接到数据库")
            return conn
    except mysql.connector.Error as err:
        print(f"数据库连接失败: {err}")
        return None

def save_to_database(data):
    """将数据保存到数据库"""
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()

        # 假设我们要插入的数据表结构如下：
        # CREATE TABLE flight_price_history (id INT AUTO_INCREMENT PRIMARY KEY, origin VARCHAR(100), destination VARCHAR(100), lowest_price DECIMAL(10,2), query_date DATE);
        insert_query = """
        INSERT INTO flight_price_history (origin, destination, flydate, price, discount, flightno, flytime, arrtime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            created_at = CURRENT_TIMESTAMP
        """
        
        try:
            cursor.executemany(insert_query, data)  # 批量插入数据
            conn.commit()
            print(f"成功保存或更新了{len(data)} 条数据到数据库")
        except mysql.connector.Error as err:
            print(f"插入数据失败: {err}")
        finally:
            cursor.close()
            conn.close()
            
def fetch_flight_data():
    """爬取网页并提取数据"""
    url = "https://www.ly.com/flights/api/getpricecalendar" 
    
    headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Origin': 'https://www.ly.com',
    'Referer': 'https://www.ly.com/flights/itinerary/oneway/BJS-SHA?date=2024-12-26&from=%E5%8C%97%E4%BA%AC&to=%E4%B8%8A%E6%B5%B7&refid=2000118609',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json;charset=UTF-8',
    'refid': '2000118609',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'tcplat': '1',
    'tcsectoken': '',
    'tcsessionid': 'nologin-1735218009100',
    'tctracerid': 'nologin-1735218009100',
    'tcuserid': '',
    'tcversion': '1.1.0',
    }


    with open('filtered_getallcityandairports.json', 'r', encoding='utf-8') as file:
        city_data = json.load(file)
    #print(city_data)

    # 获取所有有效的 cityCode（跳过 airportName 和 airportShortName 都为空的城市）
    city_codes = ['BJS','TSN','SHA','WSK','SJW','TYN','SHE','CGQ','HRB','NKG','HGH','HFE','FOC','KHN','TNA',
                  'CGO','WUH','CSX','CAN','HAK','CTU','KWE','KMG','SIA','LHW','XNN','URC','LXA','HET','INC','NNG','HKG','MFM','TPE']
    # for group in data['body']:
    #     for city in data['body'][group]:
    #         if not (city['airportName'] == "" and city['airportShortName'] == ""):
    #             city_codes.append(city['cityCode'])

    for start_port in city_codes:
        for end_port in city_codes:
            if start_port != end_port:
                # print(f"StartPort: {start_port}")
                # print(f"EndPort: {end_port}")
                time.sleep(0.1)
                query_beg_date = datetime.now().strftime('%Y-%m-%d')
                query_end_date = (datetime.now() + timedelta(days=59)).strftime('%Y-%m-%d')
                # print(f"QueryBegDate: {query_beg_date}")
                # print(f"QueryEndDate: {query_end_date}")
                json_data = {
                'StartPort': start_port,
                'EndPort': end_port,
                'QueryBegDate': query_beg_date,
                'QueryEndDate': query_end_date,
                'QueryType': 1,
                'travelTypes': [
                    1,
                ],
                'flat': 1,
                'plat': 1,
                'isFromKylin': 1,
                'refid': '2000118609',
                }
                print(json_data)

                session = requests.Session()
                session.post(url=url, headers=headers)
                # 发起请求
                response = session.post(url=url, headers=headers, json=json_data)
                if response.status_code == 200:
                
                    # 解析 JSON 数据
                    data = response.json()
                
                    # 检查 "body" 是否存在
                    if "body" in data and "fzpriceinfos" in data["body"]:
                        flight_data = []
                        fzpriceinfos = data["body"]["fzpriceinfos"]
                        startportname = data["body"].get("startportname", "")  # 获取起点名称
                        endportname = data["body"].get("endportname", "")  # 获取终点名称

                        # 提取航班信息
                        for item in fzpriceinfos:
                            flydate = item.get("flydate", "")
                            price = item.get("price", 0)
                            discount = item.get("discount", 0)
                            flightno = item.get("flightno", "")
                            flytime = item.get("flytime", "")
                            arrtime = item.get("arrtime", "")
                        
                            # 添加数据到 list 中
                            flight_data.append((startportname, endportname, flydate, price, discount, flightno, flytime, arrtime))
                    
                        # 保存数据到数据库
                        save_to_database(flight_data)
                    else:
                        print("返回的数据格式不正确或没有航班信息")
                else:
                    print(f"请求失败，状态码: {response.status_code}")

# if __name__ == "__main__":
#     fetch_flight_data()

def job():
    print("开始执行抓取程序...")
    fetch_flight_data()
    print("抓取程序执行完毕。")

schedule.every().day.at("20:40").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)