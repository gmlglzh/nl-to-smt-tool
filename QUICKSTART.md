# 快速入门指南（5分钟上手）

## 第 1 步：安装（2 分钟）

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/nl-to-smt-tool.git
cd nl-to-smt-tool

# 安装依赖
pip install -r requirements.txt

# 测试安装
python test_installation.py
```

如果看到 "All tests passed!"，说明安装成功。

## 第 2 步：获取 API Key（1 分钟）

1. 访问 https://platform.deepseek.com
2. 注册/登录
3. 创建 API Key
4. **复制保存**（只显示一次）

## 第 3 步：启动工具（1 分钟）

```bash
python app.py
```

看到 "Running on http://0.0.0.0:5000" 后，打开浏览器访问：
```
http://localhost:5000
```

## 第 4 步：使用示例（1 分钟）

### 方法 A：加载内置示例

1. 点击 "Load Example" 按钮
2. 填入你的 API Key
3. 点击 "Generate JSON"
4. 等待 10-15 秒
5. 查看生成的 Blueprint 和 Encoder Plan

### 方法 B：输入自己的策略

在 NL Policy 输入框输入：

```
在线支付系统策略：

1. 支付前必须验证用户身份和检查余额
2. 高风险交易需要短信验证码确认
3. 如果检测到异常行为，系统进入风控模式
4. 风控模式下，所有交易都需要人工审核
5. 风控模式持续直到异常解除
```

然后点击 "Generate JSON"。

## 第 5 步：验证和测试

### 验证 JSON

点击 "Validate JSON" 按钮，查看：
- ✓ JSON 格式正确
- SAT/UNSAT 结果
- 约束数量

### 测试场景（可选）

点击 "Test Scenario"，输入测试场景：

```json
{
  "prefix_length": 2,
  "events": [
    {"time": 0, "event": "异常行为检测"},
    {"time": 1, "event": "支付请求"}
  ],
  "states": [],
  "check": {"require_eventually": "人工审核"}
}
```

查看是否 UNSAT（因为风控模式下需要审核）。

### 下载结果

点击 "Download JSON" 保存生成的策略。

---

## 常见问题

### Q: 生成失败怎么办？
- 检查 API Key 是否正确
- 确认网络连接正常
- 尝试简化策略描述

### Q: 生成的 JSON 有错误？
- **正常！** LLM 生成约 85% 正确
- 手动编辑修正即可
- 参考右侧的模板文档

### Q: 如何修改生成结果？
- 直接在文本框编辑 JSON
- 修改后点击 "Validate JSON" 验证
- 确认无误后点击 "Download JSON"

### Q: 端口被占用？
编辑 `app.py` 最后一行：
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 改成 5001
```

---

## 完整工作流示例

```
输入 NL:
"发送邮件前必须获得审批。紧急模式下禁止自动发送。"

↓ [LLM 生成]

Blueprint:
{
  "events": ["approval_received", "email_sent", "emergency_activated"],
  "states": ["emergency_mode_active"]
}

↓ [人工审查]

修正: "emergency_activated" → 应该是状态不是事件

↓ [编辑 JSON]

Encoder Plan:
{
  "temporal_constraints": [
    {
      "kind": "always_previously_requires",
      "trigger": "email_sent",
      "all_before": ["approval_received"]
    },
    {
      "kind": "always_prevents_while_state",
      "state": "emergency_mode_active",
      "event": "email_sent"
    }
  ]
}

↓ [验证]

✓ SAT (可满足)

↓ [下载保存]
```

---

## 下一步

- 阅读 **README.md** 了解完整功能
- 查看 **GITHUB_UPLOAD_GUIDE.md** 学习如何分享
- 阅读 **PROJECT_SUMMARY.md** 了解技术细节

---

🎉 **恭喜！你已经学会使用 NL to SMT Tool 了！**
