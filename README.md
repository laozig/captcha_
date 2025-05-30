# 极简验证码识别工具

一个简单易用的验证码识别工具，支持图形验证码和滑块验证码。

## 功能特点

- 支持常见图形验证码自动识别
- 支持滑块验证码自动拖动（包括拼图滑块）
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

### 3. 获取代码

#### 克隆仓库

```bash
# 使用HTTPS克隆
git clone https://github.com/laozig/captcha_.git

# 使用SSH克隆
git clone git@github.com:laozig/captcha_.git
```

#### 下载ZIP压缩包

你也可以直接下载ZIP压缩包：

```bash
# 使用curl下载
curl -L https://github.com/laozig/captcha_/archive/refs/heads/main.zip -o captcha_.zip

# 使用wget下载
wget https://github.com/laozig/captcha_/archive/refs/heads/main.zip -O captcha_.zip
```

或者直接访问 [下载链接](https://github.com/laozig/captcha_/archive/refs/heads/main.zip)

### 4. 更新和贡献代码

#### 更新本地代码

如果你已经克隆了仓库，可以通过以下命令更新到最新版本：

```bash
# 进入项目目录
cd captcha_

# 获取远程更新
git fetch origin

# 合并最新代码
git pull origin main
```

#### Fork和贡献代码

如果你想贡献代码，可以按照以下步骤操作：

1. 在GitHub上Fork本仓库
2. 克隆你的Fork仓库到本地

```bash
git clone https://github.com/你的用户名/captcha_.git
```

3. 创建新的分支

```bash
git checkout -b feature/你的功能名称
```

4. 提交你的修改

```bash
git add .
git commit -m "添加新功能：功能描述"
git push origin feature/你的功能名称
```

5. 在GitHub上创建Pull Request

访问你Fork的仓库页面，点击"Pull Request"按钮，创建一个新的Pull Request，描述你的修改内容。

### 5. 启动OCR服务器

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
