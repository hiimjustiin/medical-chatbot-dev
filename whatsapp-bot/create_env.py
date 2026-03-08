#!/usr/bin/env python3
"""
创建干净的.env文件脚本
"""

def create_clean_env():
    """创建干净的.env文件"""
    env_content = """# Meta WhatsApp Business API 配置
META_ACCESS_TOKEN=EAAOb7mIZAz9EBPZAtuD5i80AHZBimRY4NjWSyXtvMzZCYNNjbOHepMG3gfxUl41zTt9fK1BtXOWa2SgGVmWtANK5Rju7GwcaTp5ZBM24mmXeRVZB39irIEfaroNtH7SVl3681gONvXEYycBNzTQO3KIrOYZCMsGlqBY8i7q0KEOSrWcySx08WTXA2gZCPWdR2ZAucsvMjUSZBnAqueUl8BrZCaHocmXtTUDbXb38hzoOOoH
META_VERIFY_TOKEN=my_custom_verify_token_123
META_PHONE_NUMBER_ID=1015873080512465
META_BUSINESS_ACCOUNT_ID=693072067109120
FORWARD_URL=http://localhost:3005/api/data/chat/message
USE_META_API=true"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ 成功创建干净的 .env 文件")
        return True
    except Exception as e:
        print(f"❌ 创建 .env 文件失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧹 创建干净的 .env 文件...")
    if create_clean_env():
        print("🎉 完成！现在可以运行测试了")
    else:
        print("❌ 失败")
