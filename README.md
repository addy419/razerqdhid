
# Razer Quick&Dirty HID

Changes configuration of Razer Basilisk V3 with analyzed reverse-engineered protocol. The project doesn't use proprietary code in Razer Synapse software. It uses python with [libusb/hidapi](https://github.com/libusb/hidapi) to communicate with the mouse, so it's cross-platform.

The implementation is easy, and its main functionality is to be able to bind mouse buttons with on board memory, and can read and alter macros, which other softwares haven't implemented.

The project borrows some definitions and command values from [CalcProgrammer1/OpenRGB](https://gitlab.com/CalcProgrammer1/OpenRGB) and [openrazer](https://github.com/openrazer/openrazer), but other than that, it doesn't use any code from those projects.

更改 Razer Basilisk V3 (雷蛇巴蛇V3) 鼠标配置，使用抓包分析到的协议，没有借助雷蛇任何软件的代码。使用 Python 调用 [libusb/hidapi](https://github.com/libusb/hidapi) 通信，可跨平台使用。实现比较简单，主要是可以更改按键功能，可以读取和修改宏（巨集），其他开源软件没有实现。

借鉴了 [CalcProgrammer1/OpenRGB](https://gitlab.com/CalcProgrammer1/OpenRGB) 和 [openrazer](https://github.com/openrazer/openrazer) 的函数名、命令数值等，但是完全没有使用那些代码。

## 使用方法 / Usage method

Front-end application:

Written with Vue.js. You can use Node.js to `npm install` and run `npm run dev` to launch development server. Or you can directly visit public site under GitHub descriptions.

Python backend:

It's located in [py directory](./public/py/), and it can be used independent of front-end part.

You should download [libusb/hidapi](https://github.com/libusb/hidapi), put it in a place python can detect, then use pip to install <https://pypi.org/project/hid/>.

前端应用：

使用 Vue 编写。使用 Node.js `npm install` 以后，使用 `npm run dev` 启动开发服务器，即可使用。或直接访问 GitHub 简介下方的网址。

Python 后端：位于 [py 目录](./public/py/)中，可以独立运行。

下载 [libusb/hidapi](https://github.com/libusb/hidapi)，放到 Python 可以加载的位置。使用 pip 安装 <https://pypi.org/project/hid/>。

## 协议逆向文档 / Reverse-engineer documentation

The protocol and command list analyzed is [this documentation](./docs/basic.md).

分析出的协议和命令列表见[协议逆向文档](./docs/basic.md)
