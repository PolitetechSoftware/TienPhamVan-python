from rabbitmq_config import channel
import json
from .db_config import cur, conn


def check_table_exists(table_name):
    list_tables = cur.execute(
        f"""SELECT tbl_name FROM sqlite_master WHERE type='table'
        AND tbl_name='{table_name}'; """).fetchall()

    if list_tables == []:
        return False
    else:
        return True


def insert_data(ch, method, properties, body):
    data = json.loads(body.decode())
    print(f" [x] Received {data}")

    list_function = cur.execute(
            f"""SELECT * from m_metrics where function_name = '{data["function_name"]}'"""
        ).fetchall()

    exec_time = data["stop_time"] - data["start_time"]

    # Insert detail metrics
    cur.execute(f"""INSERT INTO t_metrics
                    VALUES(
                    '{data["function_name"]}', '{data["exec_date"]}', {data["error"]}, {exec_time})""")
    
    if list_function == []:
        # Insert master metrics
        cur.execute(f"""INSERT INTO m_metrics
                    VALUES('{data["function_name"]}', 1, {data["error"]}, {exec_time})""")
    else:
        errors_cnt = list_function[0][2] + data["error"]
        number_call = list_function[0][1] + 1

        # Get average of execution time
        exec_time_avg = cur.execute(
            f"""SELECT avg(exec_time) from t_metrics where function_name = '{data["function_name"]}'"""
        ).fetchall()
        # Update master metrics
        cur.execute(f"""UPDATE m_metrics
                    SET number_call = {number_call}, errors_cnt = {errors_cnt},
                    exec_time_avg = {exec_time_avg[0][0]} WHERE function_name = '{data["function_name"]}'""")

    conn.commit()
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)


# Create table m_metrics if not exists
if check_table_exists("m_metrics") is False:
    cur.execute(""" CREATE TABLE m_metrics (
                function_name TEXT NOT NULL PRIMARY KEY,
                number_call INTEGER NOT NULL DEFAULT 0,
                errors_cnt INTEGER NOT NULL DEFAULT 0,
                exec_time_avg REAL NOT NULL DEFAULT 0
            ); """)


# Create table t_metrics if not exists
if check_table_exists("t_metrics") is False:
    cur.execute(""" CREATE TABLE t_metrics (
            function_name TEXT NOT NULL,
            exec_date TEXT NOT NULL,
            error_flg INTEGER NOT NULL DEFAULT 0,
            exec_time REAL NOT NULL DEFAULT 0,
            PRIMARY KEY (function_name, exec_date)
        ); """)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.basic_consume(queue='metrics', on_message_callback=insert_data)
channel.start_consuming()

