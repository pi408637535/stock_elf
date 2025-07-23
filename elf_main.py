# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import efinance as ef
import pymysql
import pandas as pd
import smtplib  # 导入PyEmail
from email.mime.text import MIMEText
import time
from datetime import datetime
import sys
import socket
from pymysql.cursors import DictCursor
import random

class MySqlQuery():
    def __init__(self, env):
        self.localhost = '43.156.232.204' if env == 'local' else '127.0.0.1'
        self.cursor = self.mycursor()
    def mycursor(self, db_name='stock_db'):
        connection = pymysql.connect(host=self.localhost,
                                     user='root',
                                     port=3306,
                                     password='897huvcasdef_a',  # 123456
                                     database=db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        connection.autocommit(True)
        cursor = connection.cursor()
        self.conn = connection
        return cursor
    def query(self, sql):

        '''以数据框形式返回查询据结果'''
        self.cursor.execute(sql)
        data = self.cursor.fetchall()  # 以元组形式返回查询数据
        header = [t[0] for t in self.cursor.description]
        df = pd.DataFrame(list(data), columns=header)  # pd.DataFrem 对列表具有更好的兼容性
        return df
    def update(self, stock_code):
        sql = "update stock_db.stock_elf set status=0, update_at = '{1}' where stock_code='{0}'".format(stock_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.cursor.execute(sql)
        self.conn.commit()

    def get_sentry_id(self, cdate):
        sql = "select id from sentry_monitor   where cdate = \'{0}\'".format(cdate)
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def insert_sentry(self, cdate, sentry):
        sql = "insert into sentry_monitor(`sentry`, cdate) VALUES({0},'{1}')".format(sentry, cdate)
        self.cursor.execute(sql)
        self.conn.commit()

    def update_sentry(self, sentry_id, sentry):
        sql = "update stock_db.sentry_monitor set sentry={1} where id={0}".format(sentry_id['id'], sentry)
        self.cursor.execute(sql)
        self.conn.commit()

def get_latest_close_price(stock_code):
    # 数据间隔时间为 1 分钟
    freq = 1
    # 获取最新一个交易日的分钟级别股票行情数据
    df = None
    now = datetime.now()
    formatted_date = now.strftime("%Y%m%d")
    try:
     df = ef.stock.get_quote_history(stock_code, beg = formatted_date,
                      end = formatted_date,  klt=freq)
    except Exception as e:
        return None
    if len(df) < 0:
        return None
    latest_close_price = df.iloc[-1]['收盘']
    return latest_close_price

def send_mail(stock_code, stock_name, current_close_price, margin_price, mode):
    subject = "股市Elf-stock_code={0},stock_name={3},current_close_price={1},margin_price={2}".\
        format(stock_code, current_close_price, margin_price, stock_name)  # 邮件标题
    sender = "piguanghua365@163.com"  # 发送方
    content = "加仓" if mode == 'down' else '下单'
    recver = "piguanghua365@163.com"  # 接收方
    password = "TFDXQZXRZENQVXRZ" #邮箱密码
    message = MIMEText(content, "plain", "utf-8")
    # content 发送内容     "plain"文本格式   utf-8 编码格式

    message['Subject'] = subject  # 邮件标题
    message['To'] = recver  # 收件人
    message['From'] = sender  # 发件人

    smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
    smtp.login(sender, password)  # 发件人登录
    smtp.sendmail(sender, [recver], message.as_string())  # as_string 对 message 的消息进行了封装
    smtp.close()
    print("发送邮件成功！！")

def select_all_valid_stock(connection):
    """查询所有用户"""
    with connection.cursor() as cursor:
        sql = "select * from stock_db.stock_elf where status = 1"
        cursor.execute(sql)
        return cursor.fetchall()

def get_sentry_id(connection, cdate):
    """查询所有用户"""
    with connection.cursor() as cursor:
        sql = "select id from sentry_monitor   where cdate = \'{0}\'".format(cdate)
        cursor.execute(sql)
        return cursor.fetchone()

def insert_sentry(connection, cdate, sentry):
    sql = "insert into sentry_monitor(`sentry`, cdate) VALUES({0},'{1}')".format(sentry, cdate)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()

def update_sentry(connection, sentry_id, sentry):
    sql = "update stock_db.sentry_monitor set sentry={1} where id={0}".format(sentry_id['id'], sentry)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()

def update_stock(connection, stock_code):
    sql = "update stock_db.stock_elf set status=0, update_at = '{1}' where stock_code='{0}'".format(stock_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()

#雅虎api请求有限制，2~5秒。否则封锁
def random_sleep():
    # 随机延迟2-5秒
    wait_time = random.uniform(2, 5)
    time.sleep(wait_time)

def loop_sleep():
    current_time = datetime.now()
    formatted_time = int(current_time.strftime("%H"))
    if formatted_time >= 16 or formatted_time <= 8:
        time.sleep(60 * 60)
    else:
        time.sleep(10 * 60)

def monitor(sentry, config:dict):
    try:
        # 连接数据库
        with pymysql.connect(**config) as connection:
            print("成功连接到数据库")
            all_valid_stock = select_all_valid_stock(connection)

            meet_requirements_stock = []
            for row in all_valid_stock:
                cur_stock_price = get_latest_close_price(row['stock_code'])
                random_sleep()
                if cur_stock_price == None or cur_stock_price < 1.0:
                    print("nothing")
                    continue
                print('stock={0}, price={1}'.format(row['stock_code'], cur_stock_price))
                #下跌到
                if row['type'] == 'down' and cur_stock_price <= row['margin_price']:
                    send_mail(row['stock_code'], row['stock_name'], cur_stock_price, row['margin_price'], row['type'])
                    meet_requirements_stock.append(row['stock_code'])
                #上涨到
                if row['type'] == 'up' and cur_stock_price >= row['margin_price']:
                    send_mail(row['stock_code'], row['stock_name'], cur_stock_price, row['margin_price'], row['type'])
                    meet_requirements_stock.append(row['stock_code'])


            for ele in meet_requirements_stock:
                update_stock(connection, ele)

            print("***********loop done******************")
            loop_sleep()
            sentry += 1

            cdate = datetime.now().strftime("%Y-%m-%d")
            sentry_id = get_sentry_id(connection, cdate)
            if sentry_id == None or sentry_id['id'] == 0:
                insert_sentry(connection, cdate, sentry)
            else:
                update_sentry(connection, sentry_id, sentry)

    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

'''
0 9 * * * /root/elf.sh
'''
if __name__ == '__main__':

    # 定义主机和端口
    host = '127.0.0.1'  # 服务器IP地址，可以是 '0.0.0.0' 表示监听所有可用的网络接口
    port = 38080  # 端口号，可以选择任何未被占用的端口

    # 创建一个socket对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 将socket绑定到指定的主机和端口
    server_socket.bind((host, port))

    # 开始监听连接
    server_socket.listen(5)  # 最大连接数为5

    print(f"服务器正在监听 {host}:{port} ...")

    '''
    $ python test.py arg1 arg2 arg3
    参数个数为: 4 个参数。 
    '''
    if len(sys.argv) > 2:
        env = 'prod'
    else:
        env = 'local'
    mysql_query = MySqlQuery(env)

    sentry = 0

    localhost = '43.156.232.204' if env == 'local' else '127.0.0.1'
    config = {
        'host': localhost,
        'user': 'root',
        'password': '897huvcasdef_a',
        'database': 'stock_db',
        'charset': 'utf8mb4',
        'cursorclass': DictCursor  # 使用字典游标，返回的结果是字典形式
    }

    while True:
        monitor(sentry, config)
        sentry += 1

        # mysql_df = mysql_query.query("select * from stock_db.stock_elf where status = 1")
        # mysql_df = mysql_df[['stock_code',  'status', 'margin_price', 'type', 'stock_name']]
        # filtered_df = mysql_df[mysql_df['status'] == 1]
        #
        # for index, row in filtered_df.iterrows():
        #     cur_stock_price = get_latest_close_price(row['stock_code'])
        #     if cur_stock_price == None or cur_stock_price < 1.0:
        #         continue
        #     print('stock={0}, price={1}'.format(row['stock_code'], cur_stock_price))
        #     #下跌到
        #     if row['type'] == 'down' and cur_stock_price <= row['margin_price']:
        #         send_mail(row['stock_code'], row['stock_name'], cur_stock_price, row['margin_price'], row['type'])
        #         mysql_query.update(row['stock_code'])
        #     #上涨到
        #     if row['type'] == 'up' and cur_stock_price >= row['margin_price']:
        #         send_mail(row['stock_code'], row['stock_name'], cur_stock_price, row['margin_price'], row['type'])
        #         mysql_query.update(row['stock_code'])
        #
        # print("***********loop done******************")
        # current_time = datetime.now()
        # formatted_time = int(current_time.strftime("%H"))
        # if formatted_time >= 16 or formatted_time <= 8:
        #     # time.sleep(60 * 60)
        #     time.sleep(60 * 60)
        # else:
        #     time.sleep(1)
        # sentry += 1
        #
        # cdate = datetime.now().strftime("%Y-%m-%d")
        # sentry_id = mysql_query.get_sentry_id(cdate)
        # if sentry_id == None or sentry_id['id'] == 0:
        #     mysql_query.insert_sentry(cdate, sentry)
        # else:
        #     mysql_query.update_sentry(sentry_id, sentry)