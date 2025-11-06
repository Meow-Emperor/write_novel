# 故障排查指南

## 问题：无法创建小说 / 功能显示"即将推出"

### 快速解决方案（按顺序尝试）

#### 1. 清除浏览器缓存并强制刷新
**这是最常见的问题！**

- **Windows/Linux**: 按 `Ctrl + Shift + R` 或 `Ctrl + F5`
- **Mac**: 按 `Cmd + Shift + R`
- 或者在浏览器中：
  1. 打开开发者工具（F12）
  2. 右键点击刷新按钮
  3. 选择"清空缓存并硬性重新加载"

#### 2. 重启容器
```bash
cd D:/Code/write_novel01/write_novel-main
docker compose restart
```

等待30秒后访问：http://localhost:5173

#### 3. 完全重建容器
```bash
cd D:/Code/write_novel01/write_novel-main
docker compose down
docker compose up -d --build
```

等待1分钟后访问：http://localhost:5173

---

## 验证系统是否正常工作

### 1. 检查后端API
打开浏览器访问：http://localhost:8000/health

应该看到：
```json
{"status":"healthy","app_name":"AI Novel Platform"}
```

### 2. 测试创建小说API
在命令行运行：
```bash
curl -X POST http://localhost:8000/api/novels/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"测试小说\",\"author\":\"测试作者\"}"
```

应该返回201状态码和小说数据。

### 3. 检查前端
访问：http://localhost:5173

应该看到：
- 首页显示"AI 小说创作平台"
- 有6个功能模块卡片
- "小说管理"显示"可用"
- 其他功能显示"即将推出"（这是正常的！）

### 4. 测试创建小说（前端）
1. 点击"开始创作"或"小说管理"
2. 点击"创建新小说"
3. 填写表单：
   - 标题：测试小说
   - 作者：测试作者
   - 类型：选择任意
   - 简介：随便写点
4. 点击"保存"

**如果成功**：会显示"创建成功"，并在列表中看到新小说

**如果失败**：
- 打开浏览器开发者工具（F12）
- 切换到"Console"标签
- 查看是否有红色错误信息
- 切换到"Network"标签
- 重试创建
- 查看POST请求的响应

---

## 常见问题

### Q: 为什么其他功能显示"即将推出"？
**A**: 这是正常的！这些功能需要先选择一个小说才能使用。

**正确流程**：
1. 首页 → 小说管理
2. 创建或选择一个小说
3. 进入小说详情页
4. 在详情页可以看到所有功能都是"可用"状态

### Q: 点击功能模块没反应？
**A**: 请按照上面的流程：
- 首页的功能模块只有"小说管理"可以直接点击
- 其他功能需要在小说详情页访问

### Q: 创建小说后看不到？
**A**: 检查：
1. 是否有错误提示？
2. 刷新页面（F5）
3. 检查浏览器Console是否有错误

### Q: 后端API正常，但前端无法创建？
**A**:
1. 清除浏览器缓存（Ctrl+Shift+R）
2. 检查浏览器Console错误
3. 检查Network标签，看请求是否发送成功
4. 确认前端容器日志：`docker compose logs frontend`

---

## 检查容器状态

```bash
# 查看容器运行状态
docker compose ps

# 应该看到：
# ai-novel-backend    Up (healthy)
# ai-novel-frontend   Up

# 查看后端日志
docker compose logs backend --tail 50

# 查看前端日志
docker compose logs frontend --tail 50
```

---

## 手动测试完整流程

### 后端测试
```bash
# 进入后端容器
docker compose exec backend python3

# 在Python shell中：
import requests

# 测试创建小说
r = requests.post('http://localhost:8000/api/novels/',
                  json={'title': '测试', 'author': '作者'})
print(r.status_code)  # 应该是 201
print(r.json())  # 应该返回小说数据

# 测试查询小说
r = requests.get('http://localhost:8000/api/novels/')
print(r.json())  # 应该看到刚创建的小说
```

### 前端测试
1. 打开 http://localhost:5173
2. 打开浏览器开发者工具（F12）
3. 切换到Console标签
4. 粘贴以下代码：

```javascript
// 测试API连接
fetch('/api/novels/')
  .then(r => r.json())
  .then(data => console.log('小说列表:', data))
  .catch(err => console.error('错误:', err))

// 测试创建小说
fetch('/api/novels/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({title: 'JS测试', author: '浏览器'})
})
  .then(r => r.json())
  .then(data => console.log('创建成功:', data))
  .catch(err => console.error('创建失败:', err))
```

---

## 仍然无法解决？

请提供以下信息：

1. **浏览器Console错误**（F12 → Console标签）
2. **Network请求详情**（F12 → Network标签 → 点击失败的请求）
3. **后端日志**：`docker compose logs backend --tail 100`
4. **前端日志**：`docker compose logs frontend --tail 100`
5. **容器状态**：`docker compose ps`

提供这些信息后，我可以帮你精确定位问题。
