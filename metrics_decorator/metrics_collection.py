import time
from datetime import datetime
import json
from .rabbitmq_config import channel
from .db_config import cur

def metrics_collector(func):
  def wrapped(*args, **kwargs):
    # Get start time
    start_time = time.time()
    now = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
    error = 0
    try:
      result = func(*args, **kwargs)
    except Exception as e:
      error = 1
      raise e
    finally:
      # Get stop time
      stop_time = time.time()
      data = {
          'function_name': func.__name__,
          'error': error,
          'exec_date': now,
          'start_time': start_time,
          'stop_time': stop_time
      }
      # Push message to queue
      channel.basic_publish(exchange='', routing_key='metrics',body=json.dumps(data))
    return result
  return wrapped


def get_metrics(func_name):
  # Fetch all data of function
  list_function = cur.execute(
            f"""SELECT * from m_metrics where function_name = '{func_name}'"""
        ).fetchall()

  # Show result
  if list_function == []:
    print(f"Function data collection not yet performed: {func_name}")
  else:
    print(f"Function: {func_name}")
    print(f"Number of calls: {list_function[0][1]}")
    print(f"Average execution time: {list_function[0][3]} seconds")
    print(f"Number of errors: {list_function[0][2]}")
