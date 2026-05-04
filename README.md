# Memory App

基于间隔重复（Spaced Repetition）的个人知识记忆工具，通过主动回忆帮你巩固学习内容。

## 截图

> 待补充

## 功能

- 以卡片为单位管理知识点，支持文字和截图混排
- 3 题一组进行主动回忆复习，自评掌握程度
- SM-2 算法自动计算每张卡片的下次复习时间
- 标签分类 + 统计面板，跟踪学习进度

## 技术栈

Vue 3 + FastAPI + PostgreSQL

## 本地运行

```bash
# 1. 创建数据库
createdb memory_app
psql -d memory_app -f backend/init_db.sql

# 2. 配置 .env 文件
cp .env.example .env   # 编辑填入数据库信息

# 3. 启动后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 4. 启动前端
cd frontend
npm install && npm run dev
```

后端 http://localhost:8000 | 前端 http://localhost:5173

## 目录

```
backend/           FastAPI 应用
  main.py          入口
  models.py        数据模型
  algorithm.py     SM-2 间隔重复算法
  init_db.sql      建表语句
frontend/src/      Vue 3 前端
  views/           页面 (Review / CardManage / TagManage)
  components/      组件 (StatsPanel)
```

## License

MIT
