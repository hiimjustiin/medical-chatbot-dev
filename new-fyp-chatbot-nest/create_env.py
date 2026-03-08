#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建NestJS项目的.env文件
"""

import os

def create_env_file():
    """创建.env文件"""
    env_content = """# NestJS 后端环境变量配置
# 请将以下占位符替换为您的实际配置值

# Supabase 配置 (必需)
SUPABASE_URL=your_supabase_url_here
SUPABASE_API_KEY=your_supabase_api_key_here

# OpenAI GPT API配置 (必需)
OPENAI_API_KEY=your_openai_api_key_here

# 服务器配置
PORT=3000
NODE_ENV=development

# 其他配置 (可选)
# 添加其他需要的环境变量...
"""

    env_file_path = ".env"
    
    try:
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ 成功创建 {env_file_path} 文件")
        print("\n📝 请编辑 .env 文件并填入您的实际配置值:")
        print("   - SUPABASE_URL: 您的Supabase项目URL")
        print("   - SUPABASE_API_KEY: 您的Supabase API密钥")
        print("   - OPENAI_API_KEY: 您的OpenAI API密钥")
        print("\n⚠️  注意: 请确保所有配置值都是有效的，否则服务将无法启动")
        
    except Exception as e:
        print(f"❌ 创建 .env 文件失败: {e}")

if __name__ == "__main__":
    create_env_file()
