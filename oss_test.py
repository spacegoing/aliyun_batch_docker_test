# -*- coding: utf-8 -*-
import oss2
import os

# Connect to OSS
auth = oss2.Auth('LTAI4FtQxdgToZv4ZsYUki9a', 'T6dfTQj9an7ERTQ0COGUixutE2xDb7')

# locate remote bucket on oss:
bucket_name = 'test-batch-comp'
endpoint = 'oss-ap-southeast-2.aliyuncs.com'
bucket = oss2.Bucket(auth, endpoint, bucket_name)

# Upload local file to OSS
up_name = 'LSE_sample_week'
local_path = './Docker/LSE_sample_week/'


def get_file_name_list(local_path):
  local_file_list = [f for f in os.listdir(local_path) if 'gz' in f]
  return local_file_list


for f in get_file_name_list(local_path):
  status = bucket.put_object_from_file(f, local_path + f)


# Download from OSS2
from itertools import islice
file_name_list = []
for b in islice(oss2. ObjectIterator(bucket), 10):
  file_name_list.append(b.key)

for f in file_name_list:
  bucket.get_object_to_file(f, f)


# Upload batch test script (log_count example)
up_path = 'log-count/log-count.tar.gz'
local_path = './batch_test/log-count.tar.gz'

status = bucket.put_object_from_file(up_path, local_path)

