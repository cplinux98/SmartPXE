from __future__ import absolute_import, unicode_literals
from smartpxe.celery import app
import redis
import ansible_runner
import time
import json
from utils.tools import AddTaskRecord
import os
import uuid
from pathlib import Path
import shutil

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, db=3)

my_playbook = """
---
- name: test host
  hosts: all
  tasks:
  - name: shell id 
    command: "ifconfig"
"""
from utils.tools import RunAnsible

def template(host, status, message):
    data = {
        "host": host,
        "status": status,
        "message": message
    }
    return json.dumps(data)

@app.task(name='run_playbook')
def run_playbook(host, name, playbook, record_id):
    print('start')
    a = RunAnsible(host)
    t = AddTaskRecord(record_id)
    task_id = a.temp_id
    t.add(task_id)
    message = '任务已经开始运行'
    try:
        r = redis.Redis(connection_pool=pool)
        r.set(task_id, template(name, "start", message))
        # events =
        for event in a.run_playbook(playbook):
            message = message + "\r\n" + event['stdout']
            r.set(task_id, template(name, "running", message))
        r.set(task_id, template(name, "end", message))
        time.sleep(5)
        print(a.clear())
        message = message + "\r\n任务已完成\r\n"
        r.psetex(task_id, 5000, message)
        # add redis value to mysql
        t.done(message)
    except Exception as e:
        print(e)
    finally:
        r.close()
    print('end')



# def make_inventory(host):
#     data = {
#         "all": {
#             "hosts": host
#         }
#     }
#     return data
#
# def write_playbook(content):
#     temp_id = str(uuid.uuid4()).replace("-", '')
#     data_dir = os.path.join("/opt", "ansible", temp_id)
#     with open(playbook_path, 'w+') as fd:
#         fd.write(my_playbook)

# materials = Materials("10.10.100.39", my_playbook)
# m = ansible_runner.run(
#     private_data_dir=materials.data_dir,
#     inventory=materials.inventory(),
#     playbook=materials.playbook(),
#     quiet=True
# )
# events = m[1].events


# class Materials:
#     """
#         mm = Metarials(host='10.10.100.39', content="")
#             mm.data_dir => "/opt/ansible/xxx/"
#             mm.inventory => {"all":{"hosts": "10.10.100.39"}}
#             mm.playbook => "/opt/ansible/xxx/playbook01.yaml"
#             mm.clear => rm -rf data_dir
#     """
#     def __init__(self, host, content):
#         self.host = host
#         self.content = content
#         self.temp_id = str(uuid.uuid4()).replace("-", '')
#         self.data_dir = os.path.join("/opt", "ansible", self.temp_id)
#         mk_data_dir = Path(self.data_dir).mkdir(parents=True, exist_ok=True)
#
#     def inventory(self):
#         data = {
#             "all": {
#                 "hosts": self.host
#             }
#         }
#         return data
#
#     def playbook(self):
#         playbook_path = os.path.join(self.data_dir, 'playbook.yaml')
#         with open(playbook_path, 'w+') as fd:
#             fd.write(self.content)
#         return playbook_path
#
#     def clear(self):
#         if Path(self.data_dir).exists():
#             shutil.rmtree(self.data_dir, ignore_errors=True)
#             return 1