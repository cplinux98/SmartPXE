## 项目简介

可以通过该平台管理计算机设备系统安装的生命周期。

## 项目技术栈

```
前端
	vue2.0 + element-ui
后端
	django3.2 + jwt + python3.8.8 + mysql5.7
	
应用到的linux服务
	dnsmasq(dhcp, tftp, dns)
	nginx

任务运行使用的技术
	ansilbe_runner
	redis
	celery
```

## 项目功能

```
该项目是为了更好的管理计算机(服务器)部署系统，使用了pxe -> ipxe网络启动方式，ipxe使用http启动速度更快。
在部署系统前：
	你可以看到待安装计算机设备的硬件信息。所以，你可以根据硬件信息对计算机设备进行分类安装；
	你也可以在对计算机设备部署操作系统前对其执行任务(例如：通过脚本实现ipmi配置、raid配置)；
在部署系统中：
	你可以看到部署的详细进度；
在部署完成后：
	你可以看到部署后的结果和部署中的进度；
```

## 项目文档与演示

项目演示 http://smartpxe_demo.linux98.com

项目文档 http://smartpxe.linux98.com

部署项目 http://smartpxe.linux98.com/document/install.html

视频演示 https://www.bilibili.com/video/BV1C34y187ph

## 项目进度

目前项目处于demo阶段，功能会陆续增加。。。

- [x] 系统安装方向
  - [x] 镜像和模板的管理
    - [x] 新增
    - [x] 编辑(仅支持模板管理)
    - [x] 查看
    - [x] 删除
  - [x] 系统部署的管理
    - [x] 硬件信息收集
    - [x] 系统部署
    - [x] 日志收集
    - [x] 保留记录
- [x] 任务系统方向
  - [x] 运行model命令
  - [x] 运行playbook命令
  - [x] 收集playbook运行结果和操作记录

下个阶段准备上线的功能：
- [ ] 硬件配置
  - [ ] ipmi配置
  - [ ] 阵列卡配置


## 参考地址

```
BootOS
https://www.xiaocoder.com/2020/03/29/build-bootos-system/

Cloud Boot
https://github.com/idcos/osinstall

archlinux
wiki.archlinux.org

创建自定义 Ubuntu 映像
https://maas.io/docs/snap/2.9/ui/creating-a-custom-ubuntu-image

基于物理服务器进行ramos定制
http://www.360doc.com/content/20/1218/13/13328254_952190955.shtml

构建内存OS，基于ubuntu
http://linuxcoming.com/blog/2019/06/21/build_ram_os.html

网络引导安装ubuntu
https://ubuntu.com/server/docs/install/netboot-amd64

自定义initramfs
https://wiki.gentoo.org/wiki/Custom_Initramfs

精通initramfs
https://www.cnblogs.com/ztguang/p/12647255.html

PXELINUX
https://wiki.syslinux.org/wiki/index.php?title=PXELINUX

Redhat
https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/6/html/installation_guide/sn-booting-from-pxe-x86
```


## 开发项目

### 配置pip

```bash
mkdir ~/.pip
vim ~/.pip/pip.conf

# 输入下面的内容
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host=mirrors.aliyun.com


```

### 安装依赖包
```commandline
sudo apt install libmysqlclient-dev python3-dev gcc
pip3 install -r requirements
```

### 创建数据库

```sql
CREATE DATABASE `smartpxe` CHARACTER SET 'utf8mb4'
```

### 迁移数据库

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 创建超级用户

```bash
python3 manage.py createsuperuser
```

### 启动项目

```bash
# open dev
smartpxe.settings.py -> CONF_STATUS = 0
python3 manage.py runserver 0.0.0.0:8000
```

### build

```bash
python setup.py sdist --formats=gztar
# dist/SmartPXE-version.tar.gz
```


### install

```bash
1.从百度网盘下载 smartpxe_install_require.zip依赖文件
2.修改install.sh里面的版本号
3.将软件包放置在install.sh同级目录下
4.执行安装（root权限）
```

```angular2html
链接：https://pan.baidu.com/s/1jJJ0ZMigI7bN_8bnkz1Q-Q?pwd=m3qj 
提取码：m3qj
```

