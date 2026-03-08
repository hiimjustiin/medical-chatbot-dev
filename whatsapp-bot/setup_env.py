#!/usr/bin/env python3
"""
环境变量快速设置脚本
用于配置Meta WhatsApp Business API
"""

import os

def create_env_file():
    """创建.env文件"""
    env_content = """# Meta WhatsApp Business API 配置
META_ACCESS_TOKEN=EAAOb7mIZAz9EBPZAtuD5i80AHZBimRY4NjWSyXtvMzZCYNNjbOHepMG3gfxUl41zTt9fK1BtXOWa2SgGVmWtANK5Rju7GwcaTp5ZBM24mmXeRVZB39irIEfaroNtH7SVl3681gONvXEYycBNzTQO3KIrOYZCMsGlqBY8i7q0KEOSrWcySx08WTXA2gZCPWdR2ZAucsvMjUSZBnAqueUl8BrZCaHocmXtTUDbXb38hzoOOoH

# 验证令牌 (可以自定义，但要与Meta控制台中的设置一致)
META_VERIFY_TOKEN=my_custom_verify_token_123

# 电话号码ID
META_PHONE_NUMBER_ID=1015873080512465

# 业务账户ID
META_BUSINESS_ACCOUNT_ID=693072067109120

# 通用配置
FORWARD_URL=http://localhost:3005/api/data/chat/message

# 选择使用Meta API
USE_META_API=true
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ 成功创建 .env 文件")
        return True
    except Exception as e:
        print(f"❌ 创建 .env 文件失败: {str(e)}")
        return False

def check_env_file():
    """检查.env文件是否存在"""
    if os.path.exists('.env'):
        print("✅ .env 文件已存在")
        return True
    else:
        print("❌ .env 文件不存在")
        return False

def main():
    """主函数"""
    print("🚀 Meta WhatsApp Business API 环境变量配置")
    print("=" * 50)
    
    # 检查是否已存在.env文件
    if check_env_file():
        print("\n⚠️  .env 文件已存在，是否要覆盖？(y/n): ", end="")
        choice = input().lower().strip()
        if choice != 'y':
            print("取消操作")
            return
    
    # 创建.env文件
    if create_env_file():
        print("\n📝 环境变量配置完成！")
        print("\n🔧 下一步操作:")
        print("1. 在Meta开发者控制台设置webhook")
        print("   - URL: https://your-domain.com/webhook")
        print("   - 验证令牌: my_custom_verify_token_123")
        print("2. 运行测试脚本: python test_meta_api.py")
        print("3. 启动机器人: python main.py")
        
        print("\n⚠️  重要提醒:")
        print("- 请将 my_custom_verify_token_123 替换为您在Meta控制台中设置的实际验证令牌")
        print("- 确保webhook URL可以公开访问")
        print("- 电话号码格式: +65 8938 1527")
    else:
        print("\n❌ 配置失败，请手动创建 .env 文件")

if __name__ == "__main__":
    main()
