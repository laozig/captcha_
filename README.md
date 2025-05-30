# 极简验证码识别工具

一个简单易用的验证码识别工具，支持图形验证码、滑块验证码和图标点选验证码。

## 功能特点

- 支持常见图形验证码自动识别
- 支持滑块验证码自动拖动（包括拼图滑块）
- 支持图标点选验证码自动点击
- 轻量级设计，无需复杂配置
- 支持自定义OCR服务器地址
- 自动检测验证码和输入框
- 高准确率识别

## 安装说明

### 1. 安装油猴插件

首先需要在浏览器中安装Tampermonkey（油猴）插件：

- [Chrome插件商店](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
- [Firefox插件商店](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)
- [Edge插件商店](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd)

### 2. 安装脚本

点击下面的链接安装脚本：

[安装极简验证码识别工具](https://github.com/laozig/captcha_/raw/main/captcha_solver_lite.user.js)

### 3. 启动OCR服务器

#### Windows系统

双击运行 `start_ocr_server.cmd` 文件

#### Linux/Mac系统

```bash
chmod +x start_ocr_server.sh
./start_ocr_server.sh
```

## 使用方法

1. 启动OCR服务器
2. 打开需要识别验证码的网页
3. 脚本会自动检测并识别验证码

## 支持的验证码类型

### 图形验证码

自动识别常见的字符图形验证码，并填入对应的输入框。

### 滑块验证码

自动识别滑块验证码，计算滑动距离并模拟人工拖动完成验证。支持以下类型：
- 常规滑块验证码
- 拼图滑块验证码（需要将拼图块拖入对应缺口）

### 图标点选验证码

自动识别图标点选类验证码，分析图片中的目标位置并模拟点击。支持以下类型：
- 选择指定类型图标的验证码（如"请点击所有的汽车"）
- 顺序点击的验证码（如"请依次点击1,2,3,4"）
- 文字点选验证码（如"请点击下图中的'验证'字"）

## 配置选项

在脚本中可以修改以下配置：

```javascript
// 配置
const config = {
    autoMode: true,  // 自动识别验证码
    checkInterval: 1500,  // 自动检查间隔(毫秒)
    debug: true,  // 是否显示调试信息
    delay: 500,  // 点击验证码后的识别延迟(毫秒)
    sliderEnabled: true,  // 是否启用滑块验证码支持
    iconEnabled: true,  // 是否启用图标点选验证码支持
    // 更多配置...
};
```

## OCR服务器API

### 图形验证码识别

```
POST /ocr
Content-Type: application/json

{
    "image": "base64编码的图片数据"
}
```

### 滑块验证码识别

```
POST /slide
Content-Type: application/json

{
    "bg_image": "base64编码的背景图片",
    "slide_image": "base64编码的滑块图片"
}
```

### 图标点选验证码识别

```
POST /icon
Content-Type: application/json

{
    "image": "base64编码的图片数据",
    "prompt": "提示文本，如'请点击所有的汽车'"
}
```

## 常见问题

**Q: 验证码识别失败怎么办？**  
A: 请确保OCR服务器正常运行，并检查浏览器控制台是否有错误信息。

**Q: 如何修改OCR服务器地址？**  
A: 在脚本中修改 `OCR_SERVER` 变量的值。

**Q: 支持哪些浏览器？**  
A: 支持安装了Tampermonkey的Chrome、Firefox、Edge等主流浏览器。

## 注意事项

- 本工具仅供学习交流使用，请勿用于非法用途
- 部分网站可能有反爬虫机制，可能导致识别失败
- 请确保OCR服务器在使用前已正确启动

## 许可证

MIT License
