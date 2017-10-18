# labcontainers

manager my lab lxc containers (for gpu server)

it works but it sucks

## quick start

### 登录到远程服务器

`ssh managelxc@ip_of_remote_machine`

### 登录到你自己的账号

为了叙述清楚，此终端记为**终端A**。在终端A下，输入 `login` 之后，输入账号密码即可登录你的账号

### 创建自己的 lxc 容器

在**终端A**使用 `launch container-name` 创建并启动自己的 lxc 容器。注意，`container-name` 不能包含下划线 `_` 。

**注** ：`launch`包含两个动作：`create` + `start`。

### 更改容器密码

在**终端A中**输入 `passwd -n container-name -p newpassword`。

**在更改密码前需要启动容器**

### 查看映射的端口号

在**终端A**中输入`details`，查看相应容器的端口号。可以关闭**终端A**了

### 登录到容器中

**打开终端B**，输入下面的命令登录

```bash
ssh ubuntu@ip_of_remote_machine -p PORT
```

**这里的ip_of_remote_machine 是第一步中的ip**， 而不是`details`命令中的显示的ip，PORT为上一步中的端口号。

如果你已经能够登录，并且没有关闭相应的容器，从此，你只需要进行这一步即可登录到你的容器中。


### 其他

暂时提供了`start`/`create`/`launch`/`delete`/`stop`/`details`/`images`/`login`/`exit`/`passwd`等命令行工具。具体的，可以在终端A中，输入 `help` 相应的命令来查看帮助。

## [如何部署](/doc/how-to-deploy.md)