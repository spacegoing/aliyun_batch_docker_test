# -*- coding: utf-8 -*-
from batchcompute import Client, ClientError
from batchcompute import CN_SHENZHEN as REGION
from batchcompute.resources import (
    ClusterDescription,
    GroupDescription,
    Config,
    Networks,
    VPC,
    AppJobDescription,
    App,
    DAG,
    Mounts,
    AutoCluster,
    Disks,
    Notification,
)

access_key_id = 'LTAI4FtQxdgToZv4ZsYUki9a'  # 填写您的 AK
access_key_secret = 'T6dfTQj9an7ERTQ0COGUixutE2xDb7'  # 填写您的 AK
bucket_name = "test-batch-comp"
instance_type = "ecs.sn1.medium"  # instance type
stdoutOssPath = "oss://%s/log/stdout/" % (bucket_name)  #your stdout oss path
stderrOssPath = "oss://%s/log/stderr/" % (bucket_name)  #your stderr oss path
inputOssPath = "oss://%s/input/" % (bucket_name)  # your input oss path
outputOssPath = "oss://%s/output/" % (bucket_name)  #your output oss path


def getRuntimConfig():
  config_desc = Config()
  # 程序运行所需资源类型
  config_desc.ResourceType = "OnDemand"
  # 程序运行所需实例类型
  config_desc.InstanceType = instance_type
  # 程序运行所需实例个数
  config_desc.InstanceCount = 1
  # 实例系统盘大小，单位 GB
  config_desc.MinDiskSize = 40
  # 实例系统盘类型 cloud_efficiency/cloud_ssd
  config_desc.DiskType = "cloud_efficiency"
  # 实例数据盘大小,单位 GB
  # config_desc.MinDataDiskSize = 80
  # 实例数据盘类型，要和系统盘保持一致
  # config_desc.DataDiskType = 'cloud_efficiency'
  #实例数据盘挂载点
  # config_desc.DataDiskMountPoint = '/home/mount1/'
  # 作业失败后是否保留现场，请注意保留会继续产生费用需要及时清除
  # config_desc.ReserveOnFail = False
  # 设置作业失败重试次数
  config_desc.MaxRetryCount = 0
  # 设置作业超时时间
  config_desc.Timeout = 600
  return config_desc


def getAppJobDesc():
  job_desc = AppJobDescription()
  app_desc = App()
  # 设置job 名称
  job_desc.Name = "test-app-job"
  # test-copy app提交作业
  # 提交APP作业之前需要确保test-copy 已经创建成功，具体步骤参考APP创建流程
  app_desc.AppName = "Docker-app-demo"
  # 设置标准输入输出路径
  app_desc.Logging.StdoutPath = stdoutOssPath
  app_desc.Logging.StderrPath = stderrOssPath
  # 设置app的输入输出参数 和 test-copy APP有关
  app_desc.add_input("inputFile", inputOssPath)
  app_desc.add_output("outputFile", outputOssPath)
  # 设置作业的runtime参数
  app_desc.Config = getRuntimConfig()
  job_desc.App = app_desc
  job_desc.Type = "App"
  return job_desc


if __name__ == "__main__":
  client = Client(REGION, access_key_id, access_key_secret)
  try:
    job_desc = getAppJobDesc()
    job = client.create_job(job_desc)
    # Print out the job id.
    print(job.Id)
  except ClientError, e:
    print(e.get_status_code(), e.get_code(), e.get_requestid(), e.get_msg())
