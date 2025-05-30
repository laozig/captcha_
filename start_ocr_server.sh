#!/bin/bash

echo "===== 启动验证码识别服务 ====="

# 安装依赖
echo "安装依赖..."
pip install ddddocr fastapi uvicorn pillow opencv-python-headless numpy || pip3 install ddddocr fastapi uvicorn pillow opencv-python-headless numpy

# 启动服务
echo "正在启动验证码识别服务器..."
python3 simple_ocr_server.py

echo "服务已启动"
echo "API地址: http://localhost:9898"
echo "查看日志: ocr_server.log" 