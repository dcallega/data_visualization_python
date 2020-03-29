from influxdb import InfluxDBClient 
import time
import math
import psutil
import os
import argparse

DBNAME = 'try_db'
HOST = 'localhost'


def data_points(function, *args, **kwargs):
  x = 0
  while True:
    x += 1
    time.sleep(.1)
    f = function(x, *args, **kwargs)
    yield f

def line(x, a, b):
  return a*x + b

def sin(x, a, b):
  return a*math.sin(b*x)

def get_cpu(*args, **kwargs):
  # st = time.time()
  tmp = float(os.popen('iostat').read().split("\n")[3].split()[0])
  # print("Time to get CPU usage", time.time() - st)
  return tmp

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--host', help='IP where the database is hosted')
  parser.add_argument('--db', help='Database name (it will be created if not there)')

  args = parser.parse_args()


if __name__ == "__main__":
  args = get_args()
  data_generator = data_points(get_cpu, a=1, b=2)

  host = args.host
  db_name = args.db

  client = InfluxDBClient(host=host, port=8086, username='admin', password='admin')
  available_dbs = client.get_list_database()
  if DBNAME not in available_dbs:
    print("{} not found. Host: {}, available_dbs: {}".format(db_name, host, sorted([db["name"] for db in available_dbs])))
    in_str = input("Do you want to create it? [y/N]: ")
    if in_str.lower() == "y" or "yes" in in_str.lower():
      client.create_database(DBNAME)
  client.switch_database(DBNAME)

  try:
    start_time = time.time()
    while time.time() - start_time < 100:
      num = next(data_generator)
      posdata = [{"measurement": "function",
                  "tags": {"id": "davide"},
                  "fields": {"value": num},
                  "time": int(time.time() * 1000)}]
      client.write_points(posdata, database=DBNAME, time_precision='ms', protocol='json')
  except KeyboardInterrupt:
    print("You stopped the execution.")
  finally:
    in_str = input("Execution is finished. Do you want to delete the database? [y/N]: ")
    if in_str == "n" or in_str == "no":
      client.drop_database(dbname)
  