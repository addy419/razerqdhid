
# Razer Quick&Dirty HID

更改 Razer Basilisk V3 (雷蛇巴蛇V3) 鼠标配置，使用抓包分析到的协议，没有借助雷蛇任何软件的代码。使用 Python 调用 [libusb/hidapi](https://github.com/libusb/hidapi) 通信，可跨平台使用。实现比较简单，主要是可以更改按键功能，其他开源软件没有实现。

借鉴了 [CalcProgrammer1/OpenRGB](https://gitlab.com/CalcProgrammer1/OpenRGB) 和 [openrazer](https://github.com/openrazer/openrazer) 的函数名、命令数值等，但是完全没有使用那些代码。

## 使用方法

下载 [libusb/hidapi](https://github.com/libusb/hidapi)，放到 Python 可以加载的位置。使用 pip 安装 <https://pypi.org/project/hid/>。
目前，还没有界面，方法实现在 qdrazer 中。

## 协议

雷蛇的巴蛇v3鼠标：

四个interfaces：

- 0: endpoint 1 鼠标
  - 5个位，表示按键1-5
  - 11个位，空的
  - hid ac pan横向滚轮，8位
  - wheel，8位
  - X，Y各16位
- 1：endpoint 2 键盘
  - 键盘 id=1
    - E0~E7组合键，8位
    - 任意按键，14个8位
  - consumer control id=2
    - 16位 媒体键
    - 13个8位，空的
  - system control id=3
    - 3位，表示power down, sleep, wake up
    - 5位，空的
    - 14个8位，空的
  - 01 00 id=4
    - 15个8位
  - 01 00 id=5
    - 15个8位
- 2: endpoint 3 键盘
  - E0~E7组合键，8位
  - 任意按键，6个8位
  - LED，output, 3位
  - output，5位空的
- 3: 0x01 0xff00 vendor
  - feature 90个8位 控制信息

鼠标主动发出的信息：
- endpoint 2 id 4:
  - 应该是驱动模式下切换什么东西发的
- endpoint 2 id 5: 应该只在驱动模式下运作
  - 第一个字节为 02 切换 dpi，之后跟四个字节
  - 第一个字节为 39 切换滚动模式，跟一个字节01为自由滚动，00为触觉滚动
  - 第一个字节为 0a 和校准鼠标垫有关系，下一个字节取值有 00 和 02

发控制的信息的时候必须向 interface 3 (endpoint 0)发

主控是 https://www.nxp.com/docs/en/data-sheet/LPC51U68.pdf

这个应该已经过时了： https://github.com/mbuesch/razer/blob/master/librazer/synapse.c#L54

https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/master/Controllers/RazerController/RazerController/RazerController.h

https://github.com/openrazer/openrazer/blob/master/driver/razermouse_driver.c#L1082

union transaction_id_union
{
    unsigned char id;
    struct transaction_parts
    {
        unsigned char device : 3;
        unsigned char id : 5;
    } parts;
};

union command_id_union
{
    unsigned char id;
    struct command_id_parts
    {
        unsigned char direction : 1;
        unsigned char id : 7;
    } parts;
};

PACK(struct razer_report
{
    unsigned char               report_id;
    unsigned char               status;
    union transaction_id_union  transaction_id;
    unsigned short              remaining_packets;
    unsigned char               protocol_type;
    unsigned char               data_size;
    unsigned char               command_class;
    union command_id_union      command_id;
    unsigned char               arguments[80];
    unsigned char               crc;
    unsigned char               reserved;
});

巴蛇v3有线的 TID 是固定的 0x1f


/* Status:
 * 0x00 New Command
 * 0x01 Command Busy
 * 0x02 Command Successful
 * 0x03 Command Failure
 * 0x04 Command No Response / Command Timeout
 * 0x05 Command Not Support
 *
 * Transaction ID used to group request-response, device useful when multiple devices are on one usb
 * Remaining Packets is the number of remaining packets in the sequence
 * Protocol Type is always 0x00
 * Data Size is the size of payload, cannot be greater than 80. 90 = header (8B) + data + CRC (1B) + Reserved (1B)
 * Command Class is the type of command being issued
 * Command ID is the type of command being send. Direction 0 is Host->Device, Direction 1 is Device->Host. AKA Get LED 0x80, Set LED 0x00
 *
 * */

按键绑定：

01020001010100000000 右键绑左键
0102000e0301008e0000

- 01 保存的位置
  - 02~05 分别为红绿蓝青
- 02 要修改的硬件按键，右键
  - 01 左键
  - 02 右键
  - 03 中键下按
  - 04 侧键后面键
  - 05 侧键前面键
  - 09 滚轮上滚
  - 0a 滚轮下滚
  - 0e 底下键
  - 0f 瞄准键
  - 34 滚轮左拨
  - 35 滚轮右拨
  - 60 滚轮下远键
  - 6a 滚轮下近键
- 00 是否为 hypershift
  - 01 是 hypershift
- 01 按键类型，鼠标，键盘
  - 00 禁用
  - 01 鼠标
  - 02 键盘
  - 03 巨集宏指定次数
  - 04 按下触发宏
  - 05 切换触发宏
  - 06 dpi切换
  - 07 profile切换
  - 0a 媒体键
  - 0b 双击
  - 0c hypershift切换
  - 0d 键盘turbo
  - 0e 鼠标turbo
  - 12 滚动模式切换
  - 此外没有其他按键
- 01 后续域的长度
  - 00 禁用均为 00
- 按键值
  - 鼠标 长度 01
    - 01~05 左键~侧键后面
    - 09,0a 上滚下滚
    - 68,69 滚轮左拨右拨
  - 键盘 长度 02
    - 第一个字节为组合键
      - 01 左 ctrl
      - 02 左 shift
      - 04 左 alt
      - 10 右 ctrl
      - 20 右 shift
      - 40 右 alt
    - 第二个字节为键值
      - 04 A 05 B .. 1D Z
      - 1e 1 .. 26 9 27 0
      - 3a f1 3b f2 .. 45 f12
      - 68 f13 .. 73 f24
      - 等等，应该和 HID Scan code 一致
  - 03 巨集 长度 03
    - 7c c2 可能是巨集地址
    - 第三个字节为次数
  - 04 按下触发 长度 02
    - 7c c2
  - 05 切换触发 长度 02
    - 7c c2
  - 06 dpi切换
    - 长度01: 01 提高等级 02 降低等级 06 向上循环 07 向下循环
    - 长度05：05 意义不明，也许是表示固定 dpi，接下来四个字节，分别为XY dpi
  - 07 profile 切换 长度 01 值 04 值意义不明
  - 0a 媒体键 长度 02
    - 2个字节和 HID consumer control 的 usage code 相同
  - 0b 双击 长度 01 应该和鼠标的一致
  - 0c hypershift 切换 长度 01 值 01
  - 0d 键盘turbo 长度04 两个字节是键盘值，两个字节是 turbo 信息，延时毫秒
  - 0e 鼠标turbo 长度03 一个字节是键盘，两个字节是 turbo 信息
    - turbo 信息 7cps -> 8e, 9cps->6f，两个相乘=1000
    - 即为每次延迟的毫秒数
  - 12 滚动模式切换 长度 01 值 01

固件不知道是怎么运作的，有从固件升级器里面提取出的，但是很难分析，就不分析了

ROG 不给固件升级程序，坏坏，奥创 Armory Crate 组成太复杂了，也不好分析，而且第一次升级的时候还忘记抓包了。所以 ROG Strix Scope II RX 没固件
