#!/usr/bin/env python3
"""
启动本地Web服务器来运行CTB系统Web演示
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import subprocess
import signal
from pathlib import Path

def kill_port_processes(port=8000):
    """杀死占用指定端口的所有进程"""
    try:
        # 使用lsof查找占用端口的进程
        result = subprocess.run(['lsof', '-ti', f'tcp:{port}'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔄 发现端口 {port} 被以下进程占用: {', '.join(pids)}")
            
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    print(f"✅ 已杀死进程 {pid}")
                except subprocess.CalledProcessError:
                    print(f"⚠️  无法杀死进程 {pid} (可能已经结束)")
        else:
            print(f"✅ 端口 {port} 当前空闲")
            
    except FileNotFoundError:
        # lsof命令不存在，尝试使用netstat (虽然在macOS上lsof更常见)
        print("⚠️  lsof命令不可用，跳过端口检查")
    except Exception as e:
        print(f"⚠️  检查端口时出错: {e}")

def main():
    # 自动处理端口冲突
    print("🔍 检查端口占用情况...")
    kill_port_processes(8000)
    
    # 获取examples目录路径
    examples_dir = Path(__file__).parent.absolute()
    
    # 切换到examples目录
    os.chdir(examples_dir)
    
    # 设置端口
    port = 8000
    
    # 检查HTML文件是否存在
    ctb_file = "ctb_web_demo.html"
    time_file = "time_web_demo.html"
    
    if not os.path.exists(ctb_file):
        print(f"错误：找不到 {ctb_file}")
        print(f"当前目录：{os.getcwd()}")
        return 1
    
    if not os.path.exists(time_file):
        print(f"错误：找不到 {time_file}")
        print(f"当前目录：{os.getcwd()}")
        return 1
    
    # 创建HTTP服务器
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            ctb_url = f"http://localhost:{port}/{ctb_file}"
            time_url = f"http://localhost:{port}/{time_file}"
            
            print("=" * 70)
            print("🚀 游戏时间系统Web演示服务器已启动")
            print("=" * 70)
            print(f"📍 服务器地址: http://localhost:{port}")
            print(f"⚔️  CTB演示页面: {ctb_url}")
            print(f"🕐 时间演示页面: {time_url}")
            print(f"📁 服务目录: {examples_dir}")
            print("=" * 70)
            print("💡 提示:")
            print("  - 服务器会自动打开CTB演示页面")
            print("  - 手动访问时间演示页面查看日历系统功能")
            print("  - 按 Ctrl+C 停止服务器")
            print("  - 修改HTML文件后刷新页面即可看到更新")
            print("=" * 70)
            
            # 自动打开浏览器（同时打开两个演示页面）
            try:
                webbrowser.open(ctb_url)
                print("✅ 已打开CTB演示页面")
                # 稍微延迟后打开第二个页面，避免浏览器处理冲突
                import time
                time.sleep(0.5)
                webbrowser.open(time_url)
                print("✅ 已打开时间系统演示页面")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print(f"   请手动访问:")
                print(f"   CTB演示: {ctb_url}")
                print(f"   时间演示: {time_url}")
            
            print("\n🔄 服务器运行中，等待请求...")
            print("   (按 Ctrl+C 退出)")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 服务器已停止")
        print("=" * 60)
        return 0
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {port} 已被占用")
            print(f"   请尝试关闭其他Web服务器，或修改代码中的端口号")
            return 1
        else:
            print(f"❌ 启动服务器时出错: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 