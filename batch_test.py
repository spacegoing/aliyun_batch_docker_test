#encoding=utf-8
import sys
from batchcompute import Client, ClientError
from batchcompute import CN_SHENZHEN as REGION  #这里的region根据实际情况填写
from batchcompute.resources import (JobDescription, TaskDescription, DAG,
                                    AutoCluster)
ACCESS_KEY_ID = 'LTAI4FtQxdgToZv4ZsYUki9a'  # 填写您的 AK
ACCESS_KEY_SECRET = 'T6dfTQj9an7ERTQ0COGUixutE2xDb7'  # 填写您的 AK
IMAGE_ID = 'img-ubuntu'  #这里填写您的镜像 ID
INSTANCE_TYPE = 'ecs.sn1.medium'  # 根据实际 region 支持的 InstanceType 填写
WORKER_PATH = 'oss://test-batch-comp/log-count/log-count.tar.gz'  # 'oss://your-bucket/log-count/log-count.tar.gz'  这里填写您上传的 log-count.tar.gz 的 OSS 存储路径
LOG_PATH = 'oss://test-batch-comp/log-count/logs/'  # 'oss://your-bucket/log-count/logs/' 这里填写您创建的错误反馈和 task 输出的 OSS 存储路径
OSS_MOUNT = 'oss://test-batch-comp/log-count/'  # 'oss://your-bucket/log-count/' 同时挂载到/home/inputs 和 /home/outputs
client = Client(REGION, ACCESS_KEY_ID, ACCESS_KEY_SECRET)


def main():
  try:
    job_desc = JobDescription()
    # Create auto cluster.
    cluster = AutoCluster()
    cluster.InstanceType = INSTANCE_TYPE
    cluster.ResourceType = "OnDemand"
    cluster.ImageId = IMAGE_ID
    # Create split task.
    split_task = TaskDescription()
    split_task.Parameters.Command.CommandLine = "python split.py"
    split_task.Parameters.Command.PackagePath = WORKER_PATH
    split_task.Parameters.StdoutRedirectPath = LOG_PATH
    split_task.Parameters.StderrRedirectPath = LOG_PATH
    split_task.InstanceCount = 1
    split_task.AutoCluster = cluster
    split_task.InputMapping[OSS_MOUNT] = '/home/input'
    split_task.OutputMapping['/home/output'] = OSS_MOUNT
    # Create map task.
    count_task = TaskDescription(split_task)
    count_task.Parameters.Command.CommandLine = "python count.py"
    count_task.InstanceCount = 3
    count_task.InputMapping[OSS_MOUNT] = '/home/input'
    count_task.OutputMapping['/home/output'] = OSS_MOUNT
    # Create merge task
    merge_task = TaskDescription(split_task)
    merge_task.Parameters.Command.CommandLine = "python merge.py"
    merge_task.InstanceCount = 1
    merge_task.InputMapping[OSS_MOUNT] = '/home/input'
    merge_task.OutputMapping['/home/output'] = OSS_MOUNT
    # Create task dag.
    task_dag = DAG()
    task_dag.add_task(task_name="split", task=split_task)
    task_dag.add_task(task_name="count", task=count_task)
    task_dag.add_task(task_name="merge", task=merge_task)
    task_dag.Dependencies = {'split': ['count'], 'count': ['merge']}
    # Create job description.
    job_desc.DAG = task_dag
    job_desc.Priority = 99  # 0-1000
    job_desc.Name = "log-count"
    job_desc.Description = "PythonSDKDemo"
    job_desc.JobFailOnInstanceFail = True
    job_id = client.create_job(job_desc).Id
    print('job created: %s' % job_id)
    # job_id = 'job-000000005DA86A760000034800ED2320'
    jobInfo = client.get_job(job_id)
    while jobInfo.State == 'Waiting':
      import time
      print (jobInfo)
      time.sleep(10)
      jobInfo = client.get_job(job_id)
  except ClientError as e:
    print(e.get_status_code(), e.get_code(), e.get_requestid(), e.get_msg())


if __name__ == '__main__':
  sys.exit(main())

  '''
        {
            "CreationTime": "2019-12-20 12:54:13.065609",
            "EndTime": null,
            "Id": "job-000000005DA86A760000034800ED2320",
            "InstanceMetrics": {
                "FailedCount": 0,
                "FinishedCount": 0,
                "RunningCount": 0,
                "StoppedCount": 0,
                "WaitingCount": 5
            },
            "Message": "",
            "Name": "log-count",
            "StartTime": null,
            "State": "Waiting",
            "TaskMetrics": {
                "FailedCount": 0,
                "FinishedCount": 0,
                "RunningCount": 0,
                "StoppedCount": 0,
                "WaitingCount": 3
            }
        }
  '''
