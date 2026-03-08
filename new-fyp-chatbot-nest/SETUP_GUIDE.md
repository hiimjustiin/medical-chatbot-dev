# NestJS GPT服务设置指南

## 🚀 完整功能启动

### 1. 环境变量配置
创建 `.env` 文件并添加以下内容：

```bash
# Supabase 配置 (必需)
SUPABASE_URL=your_supabase_url_here
SUPABASE_API_KEY=your_supabase_api_key_here

# OpenAI GPT API配置 (必需)
OPENAI_API_KEY=your_openai_api_key_here

# Redis 缓存配置 (推荐)
REDIS_URL=redis://localhost:6379

# 服务器配置
PORT=3000
NODE_ENV=development
```

### 2. 启动服务
```bash
npm run start:dev
```

## 🔧 功能特性

### 完整功能包括：
- ✅ **GPT智能对话**: 基于用户运动历史提供个性化建议
- ✅ **患者管理**: 完整的患者信息管理
- ✅ **运动数据**: 运动记录和统计分析
- ✅ **数据库集成**: Supabase PostgreSQL数据库
- ✅ **用户识别**: 通过电话号码识别用户
- ✅ **周报生成**: 自动生成运动周报

## 🧪 测试GPT服务

### 测试端点
- **URL**: `http://localhost:3000/chat/message`
- **方法**: POST
- **数据格式**:
```json
{
  "From": "+65987654321",
  "Body": "你好，我想了解一些健康建议"
}
```

### 预期响应
```json
{
  "response": "GPT生成的回复内容"
}
```

## ⚠️ 注意事项

1. **完整版本**: 当前版本包含所有功能，需要Supabase和OpenAI API配置
2. **OpenAI API**: 必须配置有效的OpenAI API密钥
3. **Supabase**: 必须配置有效的Supabase URL和API密钥
4. **端口**: 服务运行在端口3000
5. **依赖**: 确保已运行 `npm install`

## 🚨 故障排除

### 常见问题

1. **OpenAI API错误**
   - 检查API密钥是否正确
   - 确认API配额是否充足

2. **Supabase连接错误**
   - 检查SUPABASE_URL和SUPABASE_API_KEY是否正确
   - 确认Supabase项目是否正常运行

3. **端口被占用**
   - 检查端口3000是否可用
   - 使用 `netstat -ano | findstr :3000` 查看

4. **依赖缺失**
   - 运行 `npm install` 安装依赖

## 📞 支持

如需帮助：
1. 检查环境变量配置
2. 查看控制台错误信息
3. 确认OpenAI API密钥有效
4. 验证端口配置

