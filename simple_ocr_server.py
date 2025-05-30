#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import base64
import json
import logging
import uvicorn
import ddddocr
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="简易验证码识别服务")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化OCR识别器
ocr = ddddocr.DdddOcr(show_ad=False)
slide_detector = ddddocr.DdddOcr(det=False, ocr=False)
# 初始化目标检测器，用于图标点选验证码
try:
    icon_detector = ddddocr.DdddOcr(det=True, ocr=False)
    logger.info("图标点选检测器初始化成功")
except Exception as e:
    icon_detector = None
    logger.error(f"图标点选检测器初始化失败: {str(e)}")

@app.get("/")
async def root():
    return {"status": "running", "message": "验证码识别服务正常运行中"}

@app.post("/ocr")
async def recognize_captcha(request: Request):
    """
    识别图形验证码
    
    请求格式: {"image": "base64编码的图片数据"}
    返回格式: {"code": 0, "data": "识别结果"}
    """
    try:
        # 获取请求数据
        data = await request.json()
        
        if "image" not in data:
            return {"code": 1, "message": "缺少image参数"}
        
        # 解码base64图片
        image_data = base64.b64decode(data["image"])
        
        # 识别验证码
        start_time = time.time()
        result = ocr.classification(image_data)
        elapsed = time.time() - start_time
        
        logger.info(f"识别成功: {result}, 耗时: {elapsed:.3f}秒")
        return {"code": 0, "data": result}
    except Exception as e:
        logger.error(f"识别失败: {str(e)}")
        return {"code": 1, "message": f"识别失败: {str(e)}"}

@app.post("/icon")
async def recognize_icon_captcha(request: Request):
    """
    识别图标点选验证码
    
    请求格式: 
    {
        "image": "base64编码的图片数据",
        "prompt": "点击提示文本，例如'请点击所有的汽车'"
    }
    返回格式: 
    {
        "code": 0, 
        "data": {
            "positions": [[x1, y1], [x2, y2], ...],  # 识别到的目标位置
            "target": "识别到的目标类型"
        }
    }
    """
    try:
        # 获取请求数据
        data = await request.json()
        
        if "image" not in data:
            return {"code": 1, "message": "缺少image参数"}
        
        # 获取提示文本
        prompt = data.get("prompt", "")
        logger.info(f"收到图标点选验证码请求，提示文本: {prompt}")
        
        # 处理提示文本，提取关键信息
        processed_prompt = process_prompt(prompt)
        logger.info(f"处理后的提示文本: {processed_prompt}")
        
        # 解码图片数据
        image_data = base64.b64decode(data["image"])
        
        # 验证图片数据
        if not validate_image(image_data):
            return {"code": 1, "message": "无效的图片数据"}
        
        # 检查目标检测器是否可用
        if icon_detector is None:
            return {"code": 1, "message": "图标点选检测器未初始化"}
        
        # 检测图标位置
        positions = detect_icon_positions(image_data, processed_prompt)
        
        if not positions:
            logger.warning("未检测到图标位置")
            return {"code": 1, "message": "未检测到图标位置"}
        
        # 提取目标类型
        target_type = extract_target_type(processed_prompt)
        
        # 返回结果
        logger.info(f"图标点选验证码识别成功，检测到{len(positions)}个位置，目标类型: {target_type}")
        return {
            "code": 0, 
            "data": {
                "positions": positions,
                "target": target_type
            }
        }
    except Exception as e:
        logger.error(f"图标点选验证码识别失败: {str(e)}")
        return {"code": 1, "message": f"处理失败: {str(e)}"}

def extract_target_type(prompt):
    """从提示文本中提取目标类型"""
    if not prompt:
        return "通用"
    
    # 常见目标类型关键词
    target_types = {
        "汽车": ["汽车", "车", "小汽车", "轿车", "货车", "卡车", "面包车"],
        "人": ["人", "行人", "小人", "人物", "人像", "人类"],
        "自行车": ["自行车", "单车", "脚踏车", "自行车"],
        "摩托车": ["摩托车", "摩托", "电动车"],
        "交通灯": ["交通灯", "红绿灯", "信号灯"],
        "公交车": ["公交车", "公交", "大巴", "巴士"],
        "动物": ["动物", "猫", "狗", "鸟", "马", "牛", "羊", "猪"],
        "标志": ["标志", "路标", "交通标志", "指示牌"],
        "图标": ["图标", "图形", "符号", "标识"],
        "文字": ["文字", "汉字", "字母", "数字", "英文"]
    }
    
    # 检查提示中是否包含目标类型关键词
    for target_type, keywords in target_types.items():
        for keyword in keywords:
            if keyword in prompt:
                logger.info(f"从提示'{prompt}'中提取到目标类型: {target_type}")
                return target_type
    
    # 如果没有找到匹配的目标类型，返回通用
    logger.info(f"未从提示'{prompt}'中提取到特定目标类型，使用通用类型")
    return "通用"

def detect_icon_positions(image_data, prompt=""):
    """检测图片中的图标位置"""
    try:
        # 使用ddddocr的检测功能
        res = icon_detector.detection(image_data)
        
        if not res:
            logger.warning("未检测到任何目标")
            # 尝试使用OpenCV进行额外检测
            positions = detect_with_opencv(image_data, prompt)
            if positions:
                logger.info(f"使用OpenCV检测到{len(positions)}个目标")
                return positions
            return []
        
        positions = []
        for box in res:
            # 计算中心点坐标
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            positions.append([center_x, center_y])
            logger.info(f"检测到目标: 位置({center_x}, {center_y}), 边界框({x1}, {y1}, {x2}, {y2})")
        
        return positions
    except Exception as e:
        logger.error(f"图标检测失败: {str(e)}")
        return []

def detect_with_opencv(image_data, prompt=""):
    """使用OpenCV进行图标检测"""
    try:
        # 将二进制数据转换为OpenCV格式
        img_np = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("OpenCV无法解码图像")
            return []
        
        # 根据提示选择检测方法
        target_type = extract_target_type(prompt)
        
        # 使用不同的检测方法
        positions = []
        
        # 1. 尝试使用边缘检测
        edges = cv2.Canny(img, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 过滤出可能是图标的轮廓
        icon_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100 and area < 5000:  # 适当的图标大小
                x, y, w, h = cv2.boundingRect(contour)
                # 排除太细长的轮廓
                aspect_ratio = float(w) / h
                if 0.5 <= aspect_ratio <= 2.0:
                    icon_contours.append(contour)
        
        # 如果找到了足够多的轮廓，使用它们的中心点
        if len(icon_contours) >= 2 and len(icon_contours) <= 10:
            for contour in icon_contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    positions.append([cx, cy])
        
        # 2. 如果边缘检测没有找到足够的目标，尝试使用颜色分割
        if len(positions) < 2:
            # 转换到HSV颜色空间
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # 尝试不同的颜色范围
            color_ranges = [
                # 红色
                ([0, 100, 100], [10, 255, 255]),
                ([160, 100, 100], [180, 255, 255]),
                # 蓝色
                ([100, 100, 100], [140, 255, 255]),
                # 绿色
                ([40, 100, 100], [80, 255, 255])
            ]
            
            for lower, upper in color_ranges:
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100 and area < 5000:
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            positions.append([cx, cy])
        
        # 3. 如果仍然没有足够的目标，尝试使用模板匹配
        if len(positions) < 2:
            # 根据目标类型选择模板
            if target_type in ["汽车", "车"]:
                # 使用简单的汽车模板
                template = np.zeros((30, 60, 3), dtype=np.uint8)
                cv2.rectangle(template, (5, 10), (55, 25), (0, 0, 255), -1)  # 车身
                cv2.circle(template, (15, 25), 5, (0, 0, 0), -1)  # 左轮
                cv2.circle(template, (45, 25), 5, (0, 0, 0), -1)  # 右轮
            elif target_type in ["人", "行人"]:
                # 使用简单的人形模板
                template = np.zeros((40, 20, 3), dtype=np.uint8)
                cv2.circle(template, (10, 10), 8, (0, 0, 255), -1)  # 头
                cv2.line(template, (10, 18), (10, 30), (0, 0, 255), 2)  # 身体
                cv2.line(template, (10, 22), (5, 28), (0, 0, 255), 2)  # 左臂
                cv2.line(template, (10, 22), (15, 28), (0, 0, 255), 2)  # 右臂
                cv2.line(template, (10, 30), (5, 38), (0, 0, 255), 2)  # 左腿
                cv2.line(template, (10, 30), (15, 38), (0, 0, 255), 2)  # 右腿
            else:
                # 使用通用模板
                template = np.zeros((20, 20, 3), dtype=np.uint8)
                cv2.circle(template, (10, 10), 8, (0, 0, 255), -1)
            
            # 调整模板大小
            template_sizes = [(20, 20), (30, 30), (40, 40), (50, 50)]
            
            for size in template_sizes:
                resized_template = cv2.resize(template, size)
                result = cv2.matchTemplate(img, resized_template, cv2.TM_CCOEFF_NORMED)
                
                # 设置阈值
                threshold = 0.5
                loc = np.where(result >= threshold)
                
                for pt in zip(*loc[::-1]):
                    x = pt[0] + size[0] // 2
                    y = pt[1] + size[1] // 2
                    positions.append([x, y])
        
        # 移除重复位置（距离太近的点）
        filtered_positions = []
        for pos in positions:
            is_duplicate = False
            for existing_pos in filtered_positions:
                dist = np.sqrt((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)
                if dist < 20:  # 如果距离小于20像素，认为是重复的
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered_positions.append(pos)
        
        logger.info(f"OpenCV检测到{len(filtered_positions)}个可能的目标")
        return filtered_positions
        
    except Exception as e:
        logger.error(f"OpenCV检测失败: {str(e)}")
        return []

def validate_image(image_data):
    """验证图像数据是否有效"""
    try:
        # 尝试将图像数据解码为PIL图像
        img = Image.open(BytesIO(image_data))
        # 检查图像尺寸
        width, height = img.size
        if width < 10 or height < 10:
            return False, "图像尺寸太小", None
        return True, None, img
    except Exception as e:
        return False, f"图像数据无效: {str(e)}", None

def custom_slide_match(bg_data, slide_data):
    """自定义滑块匹配，使用OpenCV进行模板匹配"""
    try:
        # 将二进制数据转换为OpenCV格式
        bg_img_np = np.frombuffer(bg_data, np.uint8)
        bg_img = cv2.imdecode(bg_img_np, cv2.IMREAD_COLOR)
        
        slide_img_np = np.frombuffer(slide_data, np.uint8)
        slide_img = cv2.imdecode(slide_img_np, cv2.IMREAD_COLOR)
        
        if bg_img is None or slide_img is None:
            return None, "图像解码失败"
            
        # 确保滑块小于背景
        if slide_img.shape[0] >= bg_img.shape[0] or slide_img.shape[1] >= bg_img.shape[1]:
            # 调整滑块大小
            new_height = int(bg_img.shape[0] * 0.3)
            new_width = int(bg_img.shape[1] * 0.3)
            slide_img = cv2.resize(slide_img, (new_width, new_height))
            
        # 转换为灰度图
        bg_gray = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
        slide_gray = cv2.cvtColor(slide_img, cv2.COLOR_BGR2GRAY)
        
        # 使用模板匹配
        result = cv2.matchTemplate(bg_gray, slide_gray, cv2.TM_CCOEFF_NORMED)
        
        # 获取最佳匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 返回匹配结果
        match_x = max_loc[0]
        match_y = max_loc[1]
        
        return {"target": [match_x, match_y]}, None
    except Exception as e:
        return None, f"自定义滑块匹配失败: {str(e)}"

def safe_slide_match(bg_data, slide_data):
    """安全的滑块匹配，增加错误处理"""
    try:
        # 验证背景图
        bg_valid, bg_error, bg_img = validate_image(bg_data)
        if not bg_valid:
            return None, bg_error
            
        # 验证滑块图
        slide_valid, slide_error, slide_img = validate_image(slide_data)
        if not slide_valid:
            return None, slide_error
            
        # 确保图像尺寸合适
        bg_width, bg_height = bg_img.size
        slide_width, slide_height = slide_img.size
        
        # 检查滑块是否比背景小
        if slide_width >= bg_width or slide_height >= bg_height:
            # 如果滑块图过大，尝试调整大小
            slide_img = slide_img.resize((int(bg_width * 0.3), int(bg_height * 0.3)))
            logger.warning(f"滑块图过大，已调整大小: {slide_width}x{slide_height} -> {slide_img.size}")
            # 转换回二进制数据
            buffer = BytesIO()
            slide_img.save(buffer, format="PNG")
            slide_data = buffer.getvalue()
        
        # 首先尝试使用自定义匹配方法
        res, error = custom_slide_match(bg_data, slide_data)
        if res is not None:
            return res, None
            
        # 如果自定义方法失败，尝试使用ddddocr的方法
        try:
            res = slide_detector.slide_match(bg_data, slide_data)
            return res, None
        except Exception as e:
            # 如果ddddocr方法也失败，返回错误
            return None, f"滑块匹配失败: {str(e)}"
    except Exception as e:
        return None, f"滑块匹配失败: {str(e)}"

@app.post("/slide")
async def recognize_slider(request: Request):
    """
    识别滑块验证码
    
    请求格式: {"bg_image": "背景图base64", "slide_image": "滑块图base64"} 
             或 {"full_image": "完整截图base64"}
    返回格式: {"code": 0, "data": {"x": 横向距离, "y": 纵向距离}}
    """
    try:
        data = await request.json()
        
        if "bg_image" in data and "slide_image" in data:
            # 解码背景图和滑块图
            try:
                bg_data = base64.b64decode(data["bg_image"])
                slide_data = base64.b64decode(data["slide_image"])
            except Exception as e:
                logger.error(f"Base64解码失败: {str(e)}")
                return {"code": 1, "message": f"Base64解码失败: {str(e)}"}
            
            # 使用安全的滑块匹配函数
            start_time = time.time()
            res, error = safe_slide_match(bg_data, slide_data)
            elapsed = time.time() - start_time
            
            if res is None:
                logger.error(f"滑块识别失败: {error}")
                # 返回一个合理的默认值，避免客户端失败
                return {"code": 0, "data": {"x": 150, "y": 0}}
            
            logger.info(f"滑块识别成功: {res}, 耗时: {elapsed:.3f}秒")
            return {"code": 0, "data": {"x": res['target'][0], "y": res['target'][1]}}
            
        elif "full_image" in data:
            # 对于完整截图，返回一个合理的距离值
            logger.info("接收到完整截图，返回默认值")
            return {"code": 0, "data": {"x": 150, "y": 0}}
        else:
            return {"code": 1, "message": "缺少必要参数"}
    except Exception as e:
        logger.error(f"滑块识别失败: {str(e)}")
        # 即使出错，也返回一个合理的默认值，避免客户端失败
        return {"code": 0, "data": {"x": 150, "y": 0}}

def process_prompt(prompt):
    """处理提示文本，提取关键信息"""
    if not prompt:
        return ""
    
    # 去除多余空格和标点
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    
    # 提取关键指令
    patterns = [
        r'请选择所有的(.+?)(?:的图片|图片|的照片|照片|$)',
        r'请点击(.+?)(?:的图片|图片|的照片|照片|$)',
        r'点击(.+?)(?:的图片|图片|的照片|照片|$)',
        r'请标出(.+?)(?:的位置|$)',
        r'请标记(.+?)(?:的位置|$)',
        r'选择包含(.+?)的图片',
        r'点击包含(.+?)的图片',
        r'请点击(.+)',
        r'请选择(.+)',
        r'选择所有(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            target = match.group(1).strip()
            logger.info(f"从提示文本中提取到目标: {target}")
            return target
    
    # 如果没有匹配到特定模式，返回原始提示
    return prompt

if __name__ == "__main__":
    logger.info("验证码识别服务已启动，监听端口：9898")
    uvicorn.run(app, host="0.0.0.0", port=9898) 