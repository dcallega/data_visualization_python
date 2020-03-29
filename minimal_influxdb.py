import influxdb
import time

if __name__ == "__main__":
  dbname = "test"
  client = influxdb.InfluxDBClient(host='127.0.0.1', port=8086, username='admin', password='admin')
  client.create_database(dbname)
  client.switch_database(dbname)

  num = 10
  posdata = [{"measurement": "function",
            "tags": {"id": "davide"},
            "fields": {"value": num},
            "time": int(time.time() * 1000)}]
  client.write(["{} value={}".format('function', num)], {'db':dbname},204,'line')
  client.close()
