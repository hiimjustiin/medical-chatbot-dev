import requests
import json

def test_whatsapp_send():
    """测试 WhatsApp 发送功能"""
    
    # 测试数据 - 尝试不同的号码格式
    test_data = {
        "to": "+6589422640",  # 不带 whatsapp: 前缀
        "body": "这是一条测试消息！\n\n本周运动进度报告：\n总运动时间: 120 分钟\n目标完成度: 80%\n平均心率: 75.5 bpm\n运动次数: 5 次\n\n距离本周目标还差 30 分钟，请继续加油！"
    }
    
    try:
        # 发送到 WhatsApp 机器人
        response = requests.post(
            "http://localhost:5000/send",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ WhatsApp 消息发送成功！")
        else:
            print("❌ WhatsApp 消息发送失败！")
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    print("开始测试 WhatsApp 发送功能...")
    test_whatsapp_send() 