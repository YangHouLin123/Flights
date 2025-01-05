from flask import Flask, jsonify, request
import mysql.connector
from config import DB_CONFIG
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有来源的请求

#数据库连接
def get_db_connection():
    connection = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG['port']
    )
    return connection

# 获取航班历史价格数据的 API
@app.route('/api/flight-prices', methods=['GET'])
def get_flight_prices():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    flydate = request.args.get('flydate')

    if not origin or not destination:
        return jsonify({'error': '缺少起点或终点参数'}), 400

    try:
        conn = get_db_connection()
        print("数据库连接成功")
    except mysql.connector.Error as err:
        print("数据库连接错误:", err)

    cursor = conn.cursor(dictionary=True)

    # 查询历史价格数据
    query = """
        SELECT flydate, price FROM flight_price_history 
        WHERE origin LIKE %s AND destination LIKE %s
    """

    params = (f"%{origin}%", f"%{destination}%")

    # 如果提供了飞行日期，增加日期过滤条件
    if flydate:
        query += " AND flydate <= %s"
        params += (flydate,)

    query += " ORDER BY flydate ASC"

    cursor.execute(query, params)
    results = cursor.fetchall()
    print("查询结果:", results)

    # 如果没有查询到数据，返回空列表
    if not results:
        return jsonify({'error': '未找到匹配的航班信息'}), 404

    # 格式化数据
    historical_prices = [row['price'] for row in results]
    historical_dates = [row['flydate'] for row in results]

    cursor.close()
    conn.close()

    return jsonify({'dates': historical_dates, 'prices': historical_prices})

if __name__ == '__main__':
    app.run(debug=True)
