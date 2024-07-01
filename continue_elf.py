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
        return self.conn, cursor

'''
0 9 * * * /root/elf.sh
'''
if __name__ == '__main__':



    '''
    $ python test.py arg1 arg2 arg3
    参数个数为: 4 个参数。 
    '''
    if len(sys.argv) > 2:
        env = 'prod'
    else:
        env = 'local'
    mysql_query = MySqlQuery(env)
    conn, cursor = mysql_query.mycursor()

    sentry = 0

    num = cursor.execute("select * from stock_db.stock_continue_elf_list where status = 1")
    for ele_data in cursor.fetchall():
        update_sql = 'update stock_elf set status = 1 where stock_code = {0} and `type` =  \'{1}\' '.format(ele_data['stock_code'], ele_data['type'])
        cursor.execute(update_sql)
        conn.commit()
    cursor.close()
    conn.close()

