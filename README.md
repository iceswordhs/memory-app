# Memory App — 主动回忆间隔重复学习系统

基于 SM-2 算法的个人知识记忆工具，通过主动回忆和间隔重复帮助你巩固知识。

**技术栈**: Vue 3 + FastAPI + PostgreSQL

## 功能

- **主动回忆复习**: 3 题一组，先回忆答案 → 对比正确内容 → 三档评分（熟悉/不熟悉/忘记了）
- **间隔重复算法**: 根据评分自动调整下次复习时间
- **所见即所得编辑**: 文字和截图混排，粘贴即上传
- **标签分类**: 卡片按标签筛选，颜色标记
- **统计面板**: 待复习数、完成数、正确率、连续天数

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 1. 创建数据库

```bash
createdb memory_app
psql -d memory_app -f backend/init_db.sql
```

### 2. 配置环境变量

复制并编辑 `.env` 文件：

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=你的数据库用户名
DB_PASSWORD=你的数据库密码
DB_NAME=memory_app
```

### 3. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Swagger 文档: http://localhost:8000/docs

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

## 项目结构

```
├── backend/
│   ├── main.py          # FastAPI 入口
│   ├── models.py        # 数据模型 (Card, Tag, ReviewLog)
│   ├── schemas.py       # Pydantic 校验
│   ├── crud.py          # 数据库操作
│   ├── algorithm.py     # SM-2 间隔重复算法
│   ├── config.py        # 配置读取
│   ├── database.py      # 数据库连接
│   ├── init_db.sql      # 建表语句
│   └── uploads/         # 图片上传目录
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── ReviewView.vue    # 复习页面
│       │   ├── CardManage.vue    # 卡片管理
│       │   └── TagManage.vue     # 标签管理
│       ├── components/
│       │   └── StatsPanel.vue    # 统计面板
│       ├── api/                  # API 调用
│       └── router/               # 路由
└── .env                 # 环境变量（不入库）
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/cards` | 获取卡片列表 |
| POST | `/api/cards` | 创建卡片 |
| PUT | `/api/cards/:id` | 更新卡片 |
| DELETE | `/api/cards/:id` | 删除卡片 |
| GET | `/api/tags` | 获取标签列表 |
| POST | `/api/tags` | 创建标签 |
| GET | `/api/review/next` | 获取下一组复习卡片 |
| POST | `/api/review/:card_id` | 提交复习评分 |
| POST | `/api/upload` | 上传图片 |
| GET | `/api/stats` | 获取统计数据 |

## 许可

MIT
