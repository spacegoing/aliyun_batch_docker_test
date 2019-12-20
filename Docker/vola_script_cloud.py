import gzip
import csv
from collections import defaultdict
import datetime as dt
import math  #to use the log method to calculate midpoin return
import statistics  #to use the stdev method
import glob
import oss2

# Connect to OSS
auth = oss2.Auth('LTAI4FtQxdgToZv4ZsYUki9a', 'T6dfTQj9an7ERTQ0COGUixutE2xDb7')

# locate remote bucket on oss:
bucket_name = 'test-batch-comp'
endpoint = 'oss-ap-southeast-2.aliyuncs.com'
bucket = oss2.Bucket(auth, endpoint, bucket_name)

#Read in raw data
###### Uncomment lines below only if dockerfile doesn't define workdir #####
# import os
# os.chdir('/batchcompute/workdir/data/')

# Find files
files = glob.glob('./data/*.csv.gz')

#Define variables
midpoint = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
midpoint_return = defaultdict(lambda: defaultdict(lambda: []))
intraday_volatility = defaultdict(lambda: defaultdict(lambda: None))
Market_Open = defaultdict(lambda: defaultdict(lambda: False))
start_interval_id = defaultdict(lambda: defaultdict(lambda: 0))
end_interval_id = defaultdict(lambda: defaultdict(lambda: 0))
prev_midpoint = defaultdict(lambda: defaultdict(lambda: None))
curr_midpoint = defaultdict(lambda: defaultdict(lambda: None))

#Set the interval as 5 minutes
_interval = 300


#Define a function to record midpoint price every 5 minutes
def intervals(current_date_time):
  interval = int((
      current_date_time - current_date_time.replace(hour=0, minute=0, second=0)
  ).total_seconds() // _interval)
  return interval


#Iterate the time and sales data and record midpoint every 5 minutes
for file in sorted(files):
  TAS_file = gzip.open(file, mode='rt')
  TAS_Data = csv.DictReader(TAS_file)
  for transaction in TAS_Data:
    security = transaction['#RIC']
    date = transaction['Date-Time'][:10]
    timestamp = dt.datetime.strptime(
        transaction['Date-Time'][:-7],
        '%Y-%m-%dT%H:%M:%S.%f')  #Note [-7] rounds the timestmp to milliseconds
    if transaction['Type'] == 'Mkt. Condition' and 'TRD' in transaction['Qualifiers']:
      Market_Open[date][security] = True
      start_interval_id[date][security] = intervals(timestamp)
    elif transaction['Type'] == 'Mkt. Condition' and 'CLA' in transaction['Qualifiers']:
      Market_Open[date][security] = False
      end_interval_id[date][security] = intervals(timestamp)
    if transaction['Type'] == 'Quote' and Market_Open[date][security] and transaction['Bid Price'] and transaction['Ask Price']:
      bid_price = float(transaction['Bid Price'])
      ask_price = float(transaction['Ask Price'])
      if ask_price > bid_price:
        interval_id = intervals(timestamp)
        midpoint[date][security][interval_id] = 0.5 * (ask_price + bid_price)

  out_path = f'volatility_{date}.csv'
  with open(out_path, 'w') as fh:
    output_result = csv.writer(fh)
    header = ['security', 'intraday_volatility']
    output_result.writerow(header)

    # Iterate the midpoint dictionary to calculate midpoint return and intraday-volatility
    for security in midpoint[date]:
      # looping the whole time period between market open to closing
      for interval_id in range(start_interval_id[date][security],
                               end_interval_id[date][security]):
        if prev_midpoint[date][security] is None:
          prev_midpoint[date][security] = midpoint[date][security][interval_id]
#                     print (midpoint[date][security][interval_id])
        else:
          # if the interval_id contains no midpoint, use the previous midpoint
          if not midpoint[date][security][interval_id]:
            curr_midpoint[date][security] = prev_midpoint[date][security]
          else:
            curr_midpoint[date][security] = midpoint[date][security][
                interval_id]
          midpoint_return[date][security].append(
              math.log(curr_midpoint[date][security] /
                       prev_midpoint[date][security]))
          prev_midpoint[date][security] = curr_midpoint[date][security]

      if len(midpoint_return[date][security]) > 1:
        intraday_volatility[date][security] = statistics.stdev(
            midpoint_return[date][security])
        #                     print('security=', security, 'Intraday Volatility=', intraday_volatility[date][security])
        row = [security, intraday_volatility[date][security]]
        output_result.writerow(row)


  status = bucket.put_object_from_file(out_path, out_path)
