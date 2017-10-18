## 部署指南

此程序和本实验室的需求结合比较紧密， 我已经很大限度的去除耦合了，但是缺乏经验依旧是太乱了。

### 步骤一：创建一个基础的(ubuntu) lxc image, 记录下fingerprint

建议先建立一个简单的lxc container，然后安装在lxc中安装和宿主机一样的驱动和cuda，注意，lxc应该和宿主机使用相同的方法安装nvidia驱动和cuda。

### 步骤二: 创建适用于nvidia passthrough 的 lxc profile

主要是将nvidia显卡硬件映射到lxc中，这里的profile取名随便你，我取名叫做`nvidia`。 具体需要设置那些东西，看 [这里](https://gist.github.com/khfeng/1a7fbb75f3baa0eabafb)

## 步骤三：建立初始数据, 包括数据库中的用户名和密码

修改 `add_ports_forward.sh` 内容以适应你的端口转发需要

将 `admin_example.py` 拷贝一份为 `admin.py`， 在里面修改你想修改的内容，注意你必须修改的或许只有 lxc image 的 `fingerprint` 以及那个映射nvidia硬件的`profile`。

我已经将 `admin.py` 以及 数据库 设置为gitignore，默认你的修改如果上传应该是安全的。总之请一定不要用户账号密码数据传到网上! 

### 步骤四: 创建新用户managelxc

并将其加入lxd附属组,将 managelxc 的登录shell设置为login-manager-lxc.py这个文件，请务必输入完整的路径