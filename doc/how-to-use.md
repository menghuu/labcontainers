## 使用指南

### 步骤一：登录到远程服务器

`ssh managelxc@ip_of_remote_machine`

### 步骤二: 登录到你自己的账号

为了叙述清楚，此终端记为**终端A**。在终端A下，输入 `login` 之后，输入账号密码

### 步骤三: 创建自己的 lxc 容器

在**终端A**使用 `launch container-name` 创建并启动自己的 lxc 容器。注意，`container-name` 不能包含下划线 `_` 

或者，`create container-name` 然后 `start container-name`, 其中 `container-name` 应该是你自己取得名字。

### 步骤三：更改容器密码

在**终端A中**输入 `passwd -n container-name -p newpassword`。

** 在更改密码前需要启动容器 **

在**终端A**中输入`details`，查看相应容器的端口号。**打开终端B**，输入下面的命令登录

```bash
ssh ubuntu@ip_of_remote_machine -p PORT
```

**这里的ip_of_remote_machine 是第一步中的ip**， 而不是`details`命令中的显示的ip


### 步骤四

暂时提供了`start`/`create`/`launch`/`delete`/`stop`/`details`/`images`/`login`/`exit`/`passwd`等命令行工具。具体的，可以在终端A中，输入 `help` 相应的命令来查看帮助


### 其他

如果你经历了以上过程，并且服务器没有关闭过，这辈子你都不需要经历上述的过程了