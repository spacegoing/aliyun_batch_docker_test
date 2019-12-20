#encoding=utf-8
import sys
from batchcompute import Client, ClientError
from batchcompute.resources import (JobDescription, TaskDescription, DAG,
                                    AutoCluster, GroupDescription,
                                    ClusterDescription, AppDescription)
from batchcompute import CN_BEIJING as REGION

ACCESS_KEY_ID = 'LTAI4FtQxdgToZv4ZsYUki9a'  # 填写您的 AK
ACCESS_KEY_SECRET = 'T6dfTQj9an7ERTQ0COGUixutE2xDb7'  # 填写您的 AK


def main():
  try:
    client = Client(REGION, ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    app_desc = {
        "Name": "Docker-app-demo",
        "Daemonize": False,
        "Docker": {
            "Image": "localhost:5000/vola",
            "RegistryOSSPath": "oss://test-batch-comp/dockers/"
        },
        "CommandLine": "",
    }
    appName = client.create_app(app_desc).Name
    print('App created: %s' % appName)
  except ClientError as e:
    print(e.get_status_code(), e.get_code(), e.get_requestid(), e.get_msg())


if __name__ == '__main__':
  sys.exit(main())
