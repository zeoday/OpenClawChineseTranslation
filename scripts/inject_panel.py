#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 汉化版 - 功能面板注入脚本
武汉晴辰天下网络科技有限公司 | https://qingchencloud.com/

在构建后将功能面板 JS/CSS 注入到 Dashboard 构建产物中。
"""

import os
import sys
import glob
import json
import re

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PANEL_DIR = os.path.join(ROOT_DIR, 'translations', 'panel')
BUILD_DIR = os.path.join(ROOT_DIR, 'openclaw', 'dist', 'control-ui')

def read_file(path):
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """写入文件内容"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def inject_panel():
    """注入功能面板到构建产物"""
    
    print("🦞 OpenClaw 功能面板注入")
    print("=" * 50)
    
    # 检查目录
    if not os.path.exists(BUILD_DIR):
        print(f"❌ 构建目录不存在: {BUILD_DIR}")
        sys.exit(1)
    
    assets_dir = os.path.join(BUILD_DIR, 'assets')
    if not os.path.exists(assets_dir):
        print(f"❌ assets 目录不存在: {assets_dir}")
        sys.exit(1)
    
    # 读取面板资源
    print("\n📦 读取面板资源...")
    
    panel_js_path = os.path.join(PANEL_DIR, 'feature-panel.js')
    panel_css_path = os.path.join(PANEL_DIR, 'feature-panel.css')
    panel_data_path = os.path.join(PANEL_DIR, 'panel-data.json')
    
    if not os.path.exists(panel_js_path):
        print(f"❌ 找不到 feature-panel.js: {panel_js_path}")
        sys.exit(1)
    
    panel_js = read_file(panel_js_path)
    panel_css = read_file(panel_css_path) if os.path.exists(panel_css_path) else ''
    
    # 读取并注入面板数据
    if os.path.exists(panel_data_path):
        panel_data = read_file(panel_data_path)
        # 将 PANEL_DATA 占位符替换为实际数据
        panel_js = re.sub(
            r'/\*PANEL_DATA_PLACEHOLDER\*/\{[\s\S]*?\}/\*END_PANEL_DATA\*/',
            panel_data,
            panel_js
        )
        print(f"  ✅ 已注入面板数据")
    
    print(f"  ✅ feature-panel.js ({len(panel_js)} bytes)")
    print(f"  ✅ feature-panel.css ({len(panel_css)} bytes)")
    
    # 注入 CSS 到主 CSS 文件
    print("\n🎨 注入 CSS...")
    css_files = glob.glob(os.path.join(assets_dir, '*.css'))
    css_injected = False
    
    for css_file in css_files:
        content = read_file(css_file)
        # 追加 CSS 到文件末尾
        new_content = content + '\n\n/* === OpenClaw 功能面板样式 === */\n' + panel_css
        write_file(css_file, new_content)
        print(f"  ✅ CSS 已注入: {os.path.basename(css_file)}")
        css_injected = True
    
    if not css_injected:
        print("  ⚠️ 未找到 CSS 文件，将 CSS 内嵌到 JS 中")
        # 将 CSS 转换为 JS 注入
        css_inject_code = f"""
(function() {{
  var style = document.createElement('style');
  style.textContent = {json.dumps(panel_css)};
  document.head.appendChild(style);
}})();
"""
        panel_js = css_inject_code + '\n' + panel_js
    
    # 注入 JS 到主 JS 文件
    print("\n📜 注入 JS...")
    js_files = glob.glob(os.path.join(assets_dir, '*.js'))
    js_injected = False
    
    for js_file in js_files:
        filename = os.path.basename(js_file)
        # 寻找主 bundle（通常是 index-*.js）
        if 'index-' in filename or filename == 'index.js':
            content = read_file(js_file)
            # 追加 JS 到文件末尾
            new_content = content + '\n\n/* === OpenClaw 功能面板 === */\n' + panel_js
            write_file(js_file, new_content)
            print(f"  ✅ JS 已注入: {filename}")
            js_injected = True
            break
    
    if not js_injected:
        # 如果没找到 index-*.js，尝试注入到任意 JS 文件
        for js_file in js_files:
            content = read_file(js_file)
            new_content = content + '\n\n/* === OpenClaw 功能面板 === */\n' + panel_js
            write_file(js_file, new_content)
            print(f"  ✅ JS 已注入: {os.path.basename(js_file)}")
            js_injected = True
            break
    
    if not js_injected:
        print("  ❌ 未找到可注入的 JS 文件")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 功能面板注入完成！")
    print("=" * 50)

if __name__ == '__main__':
    inject_panel()
