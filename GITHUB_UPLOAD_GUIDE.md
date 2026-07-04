# 如何上传到 GitHub

## 方法一：通过 GitHub 网页创建仓库（推荐新手）

### 第 1 步：在 GitHub 创建空仓库

1. 登录 https://github.com
2. 点击右上角 `+` → `New repository`
3. 填写信息：
   - Repository name: `nl-to-smt-tool`
   - Description: `Natural language to SMT policy translator with LLM assistance`
   - 选择 `Private` (私有) 或 `Public` (公开)
   - **不要勾选** "Add a README file"（我们已经有了）
   - **不要勾选** "Add .gitignore"（我们已经有了）
4. 点击 `Create repository`

### 第 2 步：在本地初始化 Git 并上传

打开终端，进入项目目录：

```bash
cd /home/lzh/explorer_local/nl-to-smt-tool
```

执行以下命令（按顺序）：

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件
git add .

# 3. 创建第一次提交
git commit -m "Initial commit: NL to SMT translator with web UI"

# 4. 将主分支重命名为 main（GitHub 默认）
git branch -M main

# 5. 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/nl-to-smt-tool.git

# 6. 推送到 GitHub
git push -u origin main
```

**注意**：第 5 步的命令中，把 `YOUR_USERNAME` 替换成你的 GitHub 用户名！

### 第 3 步：输入 GitHub 凭证

第一次推送时，系统会要求输入：
- **Username**: 你的 GitHub 用户名
- **Password**: 你的 GitHub Personal Access Token (PAT)

#### 如何获取 Personal Access Token：

1. GitHub → 右上角头像 → Settings
2. 左侧菜单最底部 → Developer settings
3. Personal access tokens → Tokens (classic)
4. Generate new token (classic)
5. 勾选权限：
   - `repo` (所有子项都勾选)
6. 点击 Generate token
7. **复制保存这个 token**（只显示一次！）

使用这个 token 作为密码进行推送。

---

## 方法二：通过 GitHub Desktop（图形界面）

### 第 1 步：安装 GitHub Desktop

下载：https://desktop.github.com

### 第 2 步：添加本地仓库

1. 打开 GitHub Desktop
2. File → Add local repository
3. 选择目录：`/home/lzh/explorer_local/nl-to-smt-tool`
4. 点击 "create a repository" (如果提示未初始化)

### 第 3 步：首次提交

1. 在左侧看到所有更改的文件
2. 底部输入提交信息：`Initial commit: NL to SMT translator`
3. 点击 `Commit to main`

### 第 4 步：发布到 GitHub

1. 点击顶部 `Publish repository`
2. 填写信息（名称、描述、私有/公开）
3. 点击 `Publish repository`

完成！

---

## 常用 Git 命令（日后更新代码用）

### 查看状态
```bash
git status
```

### 添加修改的文件
```bash
# 添加所有修改
git add .

# 或添加特定文件
git add app.py
```

### 提交修改
```bash
git commit -m "描述你的修改内容"
```

### 推送到 GitHub
```bash
git push
```

### 拉取最新代码（如果有合作者）
```bash
git pull
```

### 查看提交历史
```bash
git log --oneline
```

---

## 完整示例：修改代码后更新到 GitHub

```bash
# 1. 查看哪些文件被修改了
git status

# 2. 添加修改的文件
git add .

# 3. 提交修改
git commit -m "Fix: 修复了 JSON 验证的 bug"

# 4. 推送到 GitHub
git push
```

---

## 常见问题

### Q1: 提示 "remote origin already exists"
```bash
# 删除旧的 remote 再添加新的
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/nl-to-smt-tool.git
```

### Q2: 提示 "Permission denied"
- 检查 GitHub 用户名是否正确
- 确认使用的是 Personal Access Token，不是 GitHub 密码
- Token 权限是否包含 `repo`

### Q3: 推送很慢
- 可能是网络问题，使用代理或稍后再试
- 或者使用 SSH 方式（需要配置 SSH key）

### Q4: 想要撤销上次提交
```bash
# 撤销提交但保留修改
git reset --soft HEAD~1

# 撤销提交并丢弃修改（危险！）
git reset --hard HEAD~1
```

---

## 分享给老师

上传成功后，仓库地址是：
```
https://github.com/YOUR_USERNAME/nl-to-smt-tool
```

如果是私有仓库，需要：
1. 进入仓库 → Settings → Collaborators
2. 点击 `Add people`
3. 输入老师的 GitHub 用户名
4. 发送邀请

如果是公开仓库，直接把链接发给老师即可。

---

## 快速检查清单

上传前确认：
- [ ] 删除了敏感信息（API keys 等）
- [ ] .gitignore 文件正确配置
- [ ] README.md 写好了使用说明
- [ ] requirements.txt 包含所有依赖
- [ ] 代码可以正常运行

上传后确认：
- [ ] GitHub 上能看到所有文件
- [ ] README.md 在首页正确显示
- [ ] 克隆下来能正常运行
