# 要根据mac地址、系统版本、ks文件，去生成pxe菜单
import pathlib
import os
import re
import paramiko
import subprocess
import shutil
import uuid
import ansible_runner
from task.models import TaskResult
from task.serializers import TaskResultSerializer


# pxe菜单模板
text = """DEFAULT menu.c32
MENU TITLE Welcome to Custom PXE Server
PROMPT 0
TIMEOUT 30

DEFAULT Install

LABEL Install
  MENU LABEL ^Install
  MENU DEFAULT
  KERNEL {}
  INITRD {}
  APPEND ks={} {}
  IPAPPEND 2
"""




# 根据mac地址、系统版本、ks文件，去生成pxe菜单
def generate_pxe_menu(mac, kernel_path, initrd_path, ks_path, option=''):
    path = '/var/www/html/pxelinux.cfg/'
    mac = mac.replace(':', '-', 5)
    filename = '{}{}-{}'.format(path, '01', mac)
    print(filename)
    option = "inst.sshd net.ifnames=0 biosdevname=0"  # vnc vncpassword=123456
    with open(filename, 'w') as f:
        f.write(text.format(kernel_path, initrd_path, ks_path, option))
    return filename


# 根据ks文本、repo_ur、server_url 去生成符合该服务标准的ks文本内容
def replace_ks_url(old, url, server_url):
    try:
        new_repo_url = 'url --url=' + url
        new_server_url = 'server_url="' + server_url + '/install/progress/' + '${PXE_MAC}/"'
        regex_1 = re.compile('url --url=.*')
        regex_2 = re.compile('server_url=.*')
        _rest = old.replace(regex_1.findall(old)[0], new_repo_url)
        rest = _rest.replace(regex_2.findall(_rest)[0], new_server_url)
    except Exception as e:
        return 0, "ks文件内容不符合规范! \nerror : {}".format(e)
    return 1, rest

# print(replace_ks_url(long_text, 'http://xxx.xxx.xxx', 'http://sddsd.sdds.com'))

# 给BootOS发送安装指令
def send_run_rom_scripts(host, command, username="root", password="root"):
    if command == "install":
        cmd = '/usr/bin/python3 /opt/install.py'
    elif command == "shutdown":
        cmd = 'poweroff'
    elif command == "reboot":
        cmd = 'reboot'
    else:
        cmd = ''
    try:
        # username = 'root'
        # password = 'root'
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        client.connect(host, 22, username, password)
        # 执行脚本
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
    except Exception as e:
        print(e)


class ManagerDnsmasq:
    """
    /etc/dnsmasq_client/{mac}.conf
    {mac}, {ip}
    """
    def __init__(self):
        self.host_dir = pathlib.Path("/etc/dnsmasq_client/")
        self.config = "/etc/dnsmasq.conf"

    def add(self, mac, ip):
        filename = pathlib.Path(self.host_dir / "{}.conf".format(mac.replace(':', '', 5)))
        with open(filename, 'w') as fd:
            fd.write("{}, {}".format(mac, ip))

    def delete(self, mac):
        filename = pathlib.Path(self.host_dir / "{}.conf".format(mac.replace(':', '', 5)))
        print(filename)
        if pathlib.Path.exists(filename):
            os.remove(filename)
        else:
            return "file is not exists"


class RunAnsible:
    def __init__(self, host):
        self.host = host
        self.temp_id = str(uuid.uuid4()).replace("-", '')
        self.data_dir = os.path.join("/opt", "ansible", self.temp_id)
        self.inventory = self.make_inventory(self.host)
        self.make_dir = pathlib.Path.mkdir(pathlib.Path(self.data_dir), parents=True, exist_ok=True)

    @classmethod
    def make_inventory(cls, host):
        data = {
            "all": {
                "hosts": host
            }
        }
        return data

    def clear(self):
        ret = pathlib.Path(self.data_dir).exists()
        if ret:
            ret2 = shutil.rmtree(
                self.data_dir,
                # ignore_errors=True
            )
            return ('ok', ret2)
        else:
            return ('not', ret)

    def run_model(self, model=None, model_args=None):
        print(self.data_dir)
        m = ansible_runner.run(
            private_data_dir=self.data_dir,
            inventory=self.inventory,
            host_pattern="all",
            module=model,
            module_args=model_args,
            quiet=True
        )
        print(m.rc)
        stdout = m.stdout.read()
        # stderr = m.stderr.read()
        self.clear()
        # if m.rc != 0:
        #     print('error')
        #     return stderr
        return stdout

    def run_playbook(self, playbook=None):
        playbook_path = os.path.join(self.data_dir, 'playbook.yaml')
        print(playbook_path)
        with open(playbook_path, 'w+') as fd:
            fd.write(playbook)

        m = ansible_runner.run_async(
            private_data_dir=self.data_dir,
            inventory=self.inventory,
            playbook=playbook_path,
            quiet=True
        )
        events = m[1].events
        # stderr = m.stderr.read()
        return events


class AddTaskRecord:
    """
        add => add task start to mysql
        done => add task end to mysql
    """
    def __init__(self, pk):
        self.pk = pk

    def add(self, task_id):
        data = {
            "task_id": task_id,
            "progress": 2,
        }
        instance = TaskResult.objects.filter(pk=self.pk)[0]
        serializer = TaskResultSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def done(self, result):
        data = {
            "status": 0,
            "progress": 3,
            "result": result
        }
        instance = TaskResult.objects.filter(pk=self.pk)[0]
        serializer = TaskResultSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()







# class ManagerDHCP:
#     def __init__(self, host_name):
#         self.conf_file = "/etc/dhcp/dhcpd.conf"
#         self.conf = self.load_conf()
#         self.host_name = host_name
#         self.pattern = re.compile(r'host {} {{\n.*\n.*\n}}\n'.format(self.host_name), re.M|re.I)
#         self.template = """host {SN} {{\n  hardware ethernet {MAC};\n  fixed-address {IP};\n}}\n"""
#
#     def load_conf(self):
#         with open(self.conf_file, 'r') as f:
#             ret = f.read()
#         return ret
#
#     def write_conf(self):
#         with open(self.conf_file, 'w') as f:
#             f.write(self.conf)
#
#     def search(self):
#         searchOBJ = re.search(self.pattern, self.conf)
#         if searchOBJ:
#             return 1
#         else:
#             return 0
#
#     def delete(self, restart=1):
#         if self.search():
#             self.conf = re.sub(self.pattern, '', self.conf)
#             # print(self.conf)
#             if restart == 1:
#                 return self.restart_service()
#         else:
#             return 0
#
#     def add(self, mac, ip):
#         self.delete(0)
#         self.conf = self.conf + self.template.format(SN=self.host_name, MAC=mac, IP=ip)
#         print(self.conf)
#         code = self.restart_service()
#         if code == 0:
#             return code
#         return code
#
#     def restart_service(self):
#         # write self.old_conf to /etc/dhcp/dhcpd.conf
#         # if systemctl restart dhcpd ok, return 1, else return 0
#         self.write_conf()
#         code = 0
#         code = subprocess.call("dhcpd -t -q", shell=True)
#         if code != 0:
#             return 1
#         code = subprocess.call("service dhcpd restart", shell=True)
#         if code != 0:
#             return 1
#         return code