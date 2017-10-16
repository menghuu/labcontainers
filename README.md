# labcontainers

manager my lab lxc containers (for gpu server)

it works but it sucks

## 原理

使用pylxd的api操作lxc容器。lxc 容器可以和宿主机共享gpu，并且消耗的额外计算资源很少。此外使用了 zfs 以及 lxc/lxd 的特殊设计，如果我没理解错，对于空间的占用也并没有想象中的那么多。

使用数据库 sqlit3 存储用户的用户名和密码，使用 python 的 cmd 模块创建一个简单的额命令行界面。

没有对用户的 lxc 容器做任何的限定，都是最大化资源。

因为我们在一个局域网之内，所以这里我是用了 iptables 进行了端口映射，是根据每个容器的ip来映射的，所以**容器不启动，是没有端口与之对应，也就无法登录**

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

### 步骤四: 创建新用户managelxc，并将其加入lxd附属组,将 managelxc 的登录shell设置为login-manager-lxc.py这个文件，请务必输入完整的路径

## 使用指南

### 步骤一: 登录到远程服务器

`ssh managelxc@ip_of_remote_machine`

### 步骤二: 登录到你自己的账号

为了叙述清楚，此终端记为**终端A**。在终端A下，输入 `login` 之后，输入账号密码

### 步骤三: 创建自己的 lxc 容器

使用 `launch container-name` 创建并启动自己的 lxc 容器。注意，`container-name` 不能包含下划线 `_` 

或者，`create container-name` 然后 `start container-name`, 其中 `container-name` 应该是你自己取得名字。

### 步骤三：为自己的容器创建ssh私钥和公钥

在**终端A中**输入 `key container-name`。

**打开一个新的终端B**，复制 private key 部分的信息到你本机家目录下的`.ssh/id_rsa`内，复制完之后应该长这个样子
```shell
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAuOF+0qLLRZG2Tmin7JrJ6g/W5xz04y4HababA6N2EZsTndYx
SuNnabABZzqdAGt7F6aUnICt+9DsbpLEx517n6b74zVHxpX2Q+9KBP9Z0szsNuYE
OmeMzEhk1fZYX6Xn+H0WF7XkQjk4Od/Fiv6JYoa2km6lOIfqiX5UOSGb7apLqjuq
tSm0w/QsvQHG/QGBkhx6sKFDktIY2EuHfFy2s7Hck9DKgz+1N1rGQD/KUi3kJBdZ
HTSf4lnAf5NpA5qNEc4v6aLF9ww0e9C+0NqocNIpt7Holx5xgVLc202CKRHOH1gQ
rluIVmJP1VVAjhA4ADQjF61iRsQJpx9HRCHIWwIDAQABAoIBAFoqT0m271/ccobG
766qxvKKCwrnyl7JYgAieHNL0xc/BFAj2CJnyVV36xdHNK6xvHSKX0v8Td3TxJsg
pSudGF+CdrIWmAy3skTrfLP3PP1bx4/2mfVJ7xbp75OR8wOizAEaMB4cLVhGw68l
/ReOj74naP79S0LIto+btsOuKne7ky/NtyO3+CMl0PVQi02819ZVyO9GJwFHusEt
sAPEbrLTNCLhhanlIT10+eTCseGhvJUJNCeSStVXowe8QTA3c/8X+gHakAwd/T6O
vp1UjxnOYr+5QdGhQQWCG30Atm6132n4cUCRi1UxW++FRCW7LBCo4LmhNe+xcNIU
TQsytkECgYEA6bo6w8fCrYTc562oR8xzDPwozHyFz8KB2dAal30KlqOVpG7FgKXe
/q3/NWPAKns0V5Loc4xHaTx81dYe1RgZEStk9R7myocn+WlxXpl2j9VxNNwep3YI
RtluM9pj1RSNnoEK08lMbUMStShpiS+hVTi361u0d9Ks7ODLkF06NpECgYEAyn+n
pwxLVSNUjsU7yujKQgEXEoWu9AzwiEOBjTp5uHU1AlHyuh1eD5DJ7RW+7Sk0GM62
xs2qy5yZpliIczSQPF09iXZ0Iz0os3+XIPDNQe7fvhqT9oFqmQE45W832nuQdKEr
lo+nvF11HJlFle3feBwjYZJnSlYLKHjyNrSrvisCgYEA2ltEyWGX7BpDcyKXI7TL
C6eMyjXPoaDbRU2Zeku0l7VueTePxrewVIjj89IkVsvRw7sY9dJpaNS8393x4i1o
RdUfta1P+og4fVfYNYPz8z56S+MVtGeeJeq+fS0btZdFE38FSYU3pKBUGvENX8Ai
3oZltTlwqb0mFwuQwmeGmjECgYBnkw28msQ5Yt3QPL/NlG5Hfmk/txL6j1fESssL
4pn5qDGZ4zKE0ZqX2ZX+5z2F7qpP+gNxAidXB91rQSNh0cPorERaeDUFBTY5QYya
c7B5BeZ5RPzje+R7KC3i5JUr8kG79efmlcnUxfSt0RPPkSDZPYM3V/vvAL2qUNqK
8rRZiwKBgQCTPDOxcgA5+iF98uBSYqwfd3mtrHpBuFE6BG1h/pnzaEqgWVZOhAiK
Nmc7D21OR4nb08cmI3QuWGEHq9aLG/V0jqGDdmnCodirITlPltQNcpb5S8m/yfaA
OLDS10czPbCR00N03XEw3janbnig/6M8G5kCU1XtY2WYRzSEklkP5w==
-----END RSA PRIVATE KEY-----
```

注意如果你使用的是mac或者linux，需要讲此文件的权限改为600,在终端B中输入`chmod 600 $HOME/.ssh/id_rsa`。

如果你本来就已经有这个文件了，请换一个名字存储，叫什么名字存在什么地方，都无所谓。

回到刚才的**终端 A** 输入 `details`，查看对应容器的端口号，记为PORT。

回到**终端B**，输入`ssh ubuntu@ip_of_remote_machine -p PORT -i $HOME/.ssh/id_rsa`， **这里的 `-i` 之后的文件的路径应该和你存储的private key的文件路径相同**，这里的`ip_of_remote_machine` 应该是**第一步中的ip地址**，不是你在`details`中的看到的ip

如果使用的是windows，可以在类似与Putty中设置私钥的地方填入这个私钥, 然后，需要在设置端口的地方设置端口，设置好ip地址，然后就能登录了

你应该会登录到lxc容器中，请使用`sudo passwd ubuntu`修改自己的密码，(之所以这么复杂，先用key登录，是因为我并不知道怎么直接更改容器的密码)

此后，你可以不再使用private key就能登录你的容器，可以直接使用下面的命令登录你的容器

```bash
ssh ubuntu@ip_of_remote_machine -p PORT
```


### 步骤四

暂时提供了`start`/`create`/`launch`/`delete`/`stop`/`details`/`images`/`login`/`exit`等命令行工具，以我目前就发现了bug，所以请务必多多忍耐，具体的，可以在终端A中，输入 `help` 相应的命令来查看帮助


### 其他

如果你经历了以上过程，并且服务器没有关闭过，这辈子你都不需要经历上述的过程了
