```markdown
# Unicore UM982 ROS 2 Driver

这是一个适用于 **和芯星通 (Unicore) UM982** 双天线 RTK GPS 接收机的 ROS 2 驱动程序工作空间。

该驱动程序通过解析 Unicore 专有的 `PVTSLN` 消息格式，向 ROS 2 生态系统提供高频、高精度的位置和航向数据，并支持通过 RTKLIB (str2str) 进行 NTRIP 网络 RTK 差分校正。

---

## ✨ 主要特色

* **高频输出**：支持高达 20Hz 的位置和航向数据更新。
* **RTK 校正支持**：集成 NTRIP 客户端（基于 `str2str`），支持厘米级定位精度。
* **自动硬件配置**：启动时自动发送初始化指令序列。
* **串口绑定支持**：提供 Udev 规则，防止 USB 端口号（如 `/dev/ttyUSB0`）跳变。
* **标准消息格式**：发布标准的 `sensor_msgs/NavSatFix` (定位) 和 `sensor_msgs/Imu` (航向)。
* **全面诊断**：通过 `/diagnostics` 话题实时监控 GPS 健康状态。

---

## ⚙️ 环境要求

* **ROS 2 版本**：Humble / Iron / Jazzy 
* **操作系统**：Linux (推荐 Ubuntu 22.04 / 24.04)
* **硬件**：Unicore UM982 双天线 RTK GPS 接收机
* **依赖库**：
    * `rclcpp`
    * `serial_driver`
    * `sensor_msgs`
    * `geometry_msgs`
    * `diagnostic_updater`
    * `RTKLIB` (仅在使用 NTRIP 差分时需要)

---

## 🚀 安装指南

### 1. 安装 NTRIP 工具 (str2str)
如果您需要使用 RTK 网络差分，必须安装 `str2str` 工具：

```bash
sudo apt update && sudo apt install build-essential git
cd ~
git clone [https://github.com/tomojitakasu/RTKLIB.git](https://github.com/tomojitakasu/RTKLIB.git)
cd RTKLIB/app/str2str/gcc
make
sudo cp str2str /usr/local/bin/

```

### 2. 克隆与编译驱动

假设您的工作空间为 `~/ros2_ws`：

```bash
# 1. 创建并进入 src 目录
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src

# 2. 克隆本仓库
git clone [https://github.com/tang875/um982_driver_ws.git](https://github.com/tang875/um982_driver_ws.git)

# 3. 安装依赖
cd ~/ros2_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# 4. 编译
colcon build --symlink-install --packages-select unicore_um982_driver
source install/setup.bash

```

---

## 🔌 串口固定配置 (Udev)

**强烈建议配置此项！** 防止设备插拔或重启后 `/dev/ttyUSB*` 编号发生变化。

1. **复制规则文件**：
仓库中已包含配置文件，将其复制到系统目录（路径可能根据克隆后的文件夹名略有不同，请自行确认）：
```bash
# 假设克隆下来的文件夹名为 um982_driver_ws
sudo cp src/um982_driver_ws/src/tools/99-serial.rules /etc/udev/rules.d/

```


*(注：该规则默认匹配 VendorID `1a86` ProductID `7523` 的 CH340 芯片，如有不同请自行修改文件)*
2. **重载并触发规则**：
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger

```


3. **验证**：
重新插拔设备后，执行以下命令，应看到指向：
```bash
ls -l /dev/ttyGPS
# 输出应类似： lrwxrwxrwx 1 root root 7 ... /dev/ttyGPS -> ttyUSB0

```



---

## 🛠️ 配置说明

主要配置文件位于：`config/unicore_driver_params.yaml`

### 核心参数

| 参数名 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `port` | string | `/dev/ttyGPS` | **推荐**，使用 Udev 固定的设备名 |
| `baudrate` | int | `115200` | 需与 GPS 模块的波特率一致 |
| `enable_ntrip` | bool | `true` | 是否开启 NTRIP 差分 |
| `ntrip_server` | string | `rtk2go.com` | NTRIP 服务器地址 |
| `ntrip_port` | int | `2101` | NTRIP 端口 |
| `ntrip_mountpoint` | string | `FIXED` | 挂载点名称 |
| `ntrip_user` | string | `user` | 账号 |
| `ntrip_pass` | string | `password` | 密码 |

### 初始化命令

驱动会自动发送指令配置模块。如果需要修改输出频率（例如改为 20Hz），可修改 yaml 中的 `config_commands`：

```yaml
config_commands:
  - "UNLOGALL COM3"
  - "PVTSLNA COM3 1"   # 设置为 1Hz 输出，若需更高频率可改为 0.05 (20Hz)
  - "SAVECONFIG"

```

---

## ▶️ 使用方法

### 1. 启动驱动 (带 NTRIP 差分)

确保已在 yaml 中配置好 NTRIP 账号信息：

```bash
ros2 launch unicore_um982_driver unicore.launch.py

```

### 2. 启动驱动 (无 NTRIP)

仅使用单点定位：

```bash
ros2 launch unicore_um982_driver unicore.launch.py enable_ntrip:=false

```

### 3. 通过命令行覆盖参数

```bash
ros2 launch unicore_um982_driver unicore.launch.py \
  gps_port:=/dev/ttyUSB1 \
  gps_baudrate:=115200 \
  ntrip_server:=your.server.com

```

---

## 📊 话题与状态

### 发布的话题

* `/gps/fix` (`sensor_msgs/NavSatFix`): 包含经纬度、高度及协方差。
* `/gps/imu` (`sensor_msgs/Imu`): 包含航向 (Heading) 和角速度信息。
* `/diagnostics` (`diagnostic_msgs/DiagnosticArray`): 包含定位状态、卫星数量、数据延迟等。

### 定位状态说明 (Diagnostics)

* **OK (绿色)**: `RTK_FIXED` (厘米级精度，状态最佳)
* **WARN (黄色)**: `SINGLE`, `DGPS`, 或 `RTK_FLOAT` (定位中，但精度未达最高)
* **ERROR (红色)**: 无数据或连接断开

---

## ❓ 故障排除 (Troubleshooting)

### 1. 报错 `Error parsing PVTSLN message: stod`

* **原因**：接收到的数据格式有误，或者波特率不匹配导致乱码。
* **解决**：
* 检查 `baudrate` 是否与模块一致（通常为 115200 或 230400）。
* 尝试在 yaml 中将 `PVTSLNA` 改为 `PVTSLN`（取决于模块固件版本）。
* 确保天线已连接并在室外，空信号有时会导致解析器异常。



### 2. 权限被拒绝 `Permission denied: /dev/ttyGPS`

* **解决**：将当前用户加入 `dialout` 用户组：
```bash
sudo usermod -a -G dialout $USER

```


**注意**：执行后必须注销并重新登录（或重启）才能生效。

### 3. 没有 RTK Fix (一直是 SINGLE 或 FLOAT)

* 检查 NTRIP 账号是否过期。
* 检查 `str2str` 是否正在运行。
* 确保天线视野开阔，没有遮挡。

### 4. 找不到 `/dev/ttyGPS`

* 检查 USB 线是否连接紧固。
* 运行 `lsusb` 查看设备 ID 是否为 `1a86:7523`，如果不是，请修改 `99-serial.rules` 中的 ID。

---

## 📝 许可证

BSD 3-Clause License

```

```
