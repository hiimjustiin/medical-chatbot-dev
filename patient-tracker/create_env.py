#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Next.js前端的.env.local文件
"""

import os

def create_frontend_env():
    """创建前端.env.local文件"""
    env_content = """# Next.js 前端环境变量配置

# API URL - 指向NestJS后端服务
NEXT_PUBLIC_API_URL=http://localhost:3005

# Supabase 配置 (如果需要)
# NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# 其他配置
NODE_ENV=development
"""

    env_file_path = ".env.local"
    
    try:
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ 成功创建 {env_file_path} 文件")
        print("\n📝 前端环境变量配置:")
        print("   - NEXT_PUBLIC_API_URL: http://localhost:3005")
        print("   - 指向NestJS后端服务")
        print("\n⚠️  注意: 请重启前端服务以使环境变量生效")
        
    except Exception as e:
        print(f"❌ 创建 {env_file_path} 文件失败: {e}")

if __name__ == "__main__":
    create_frontend_env()










