# Implementation Plan: SkinTech AI Consultant

## Overview

本实现计划将 SkinTech AI Consultant 分解为可执行的编码任务，采用前后端分离架构。后端使用 Python FastAPI + SQLite + ChromaDB，前端使用 Next.js + Tailwind CSS。任务按依赖关系排序，确保增量开发和早期验证。

## Tasks

- [ ] 1. 项目初始化和基础设施
  - [ ] 1.1 初始化后端项目结构
    - 创建 `backend/` 目录，初始化 Python 项目 (pyproject.toml)
    - 安装依赖: fastapi, uvicorn, sqlalchemy, aiosqlite, chromadb, openai, python-jose, bcrypt, httpx
    - 创建目录结构: `app/`, `app/services/`, `app/models/`, `app/routers/`, `app/core/`
    - _Requirements: 11.1, 11.2_

  - [ ] 1.2 初始化前端项目结构
    - 创建 Next.js 项目: `npx create-next-app@latest frontend --typescript --tailwind`
    - 安装依赖: react-markdown, remark-gfm
    - 创建目录结构: `components/`, `hooks/`, `lib/`, `types/`
    - _Requirements: 10.1, 10.2_

  - [ ] 1.3 配置数据库连接
    - 创建 `app/core/database.py`，配置 SQLAlchemy async engine
    - 实现 WAL 模式配置 (PRAGMA journal_mode=WAL)
    - 创建 `app/core/config.py`，管理环境变量
    - _Requirements: 8.2, 8.3_

- [ ] 2. 数据模型和数据库 Schema
  - [ ] 2.1 创建 SQLAlchemy ORM 模型
    - 实现 User, UserProfile, Conversation, Message, SessionToken 模型
    - 创建 `app/models/` 下的所有模型文件
    - 实现数据库迁移脚本
    - _Requirements: 1.1, 2.3, 8.2, 9.3_

  - [ ] 2.2 创建 Pydantic Schema
    - 实现请求/响应模型: UserCreate, UserLogin, ChatRequest, MessageResponse
    - 实现领域模型: UserProfile, Product, IntentResult
    - 创建 `app/schemas/` 目录
    - _Requirements: 3.2, 9.2_

  - [ ]* 2.3 编写数据模型属性测试
    - **Property 4: Product Data Validity**
    - **Validates: Requirements 3.2, 3.4**

- [ ] 3. 用户认证服务
  - [ ] 3.1 实现 AuthService
    - 创建 `app/services/auth_service.py`
    - 实现 register(): bcrypt 密码哈希，创建用户
    - 实现 login(): 验证密码，生成 JWT，设置 HttpOnly Cookie
    - 实现 logout(): 清除 Cookie，记录 session_tokens 失效
    - 实现 get_current_user(): 从 Cookie 提取并验证 JWT
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6_

  - [ ] 3.2 创建认证路由
    - 创建 `app/routers/auth.py`
    - POST /api/auth/register
    - POST /api/auth/login
    - POST /api/auth/logout
    - 实现认证依赖注入 (Depends)
    - _Requirements: 11.2, 11.3_

  - [ ]* 3.3 编写认证属性测试
    - **Property 1: Password Hashing Security**
    - **Property 2: Authentication Lifecycle Round-Trip**
    - **Validates: Requirements 1.1, 1.2, 1.5, 1.6**

- [ ] 4. Checkpoint - 认证模块验证
  - 运行所有测试，确保认证流程正常
  - 验证 Cookie 设置正确 (HttpOnly, Secure, SameSite)
  - 如有问题，询问用户

- [ ] 5. 产品数据生成和摄入
  - [ ] 5.1 实现 IngestionService
    - 创建 `app/services/ingestion_service.py`
    - 实现 generate_products(): 使用 Faker 生成 5000 条产品数据
    - 实现 format_for_embedding(): 标准化文本模板
    - 实现 save_to_json(): 保存到 products_data.json
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 5.2 实现 ChromaDB 集成
    - 创建 `app/core/chroma.py`，配置 ChromaDB 客户端
    - 实现 ingest(): 向量化并存入 ChromaDB
    - 使用 OpenAI text-embedding-3-small 模型
    - _Requirements: 3.5_

  - [ ] 5.3 创建数据摄入 CLI 命令
    - 创建 `scripts/ingest_data.py`
    - 支持 --generate (生成数据) 和 --ingest (向量化) 参数
    - _Requirements: 3.1, 3.5_

  - [ ]* 5.4 编写产品数据属性测试
    - **Property 4: Product Data Validity**
    - **Validates: Requirements 3.2, 3.4**

- [ ] 6. 意图路由服务
  - [ ] 6.1 实现 IntentRouter
    - 创建 `app/services/intent_router.py`
    - 实现关键词匹配分类，计算置信度
    - 实现 LLM Fallback (gpt-4o-mini, temperature=0)
    - 返回 IntentResult (intent, confidence, used_llm_fallback)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 6.2 编写意图分类属性测试
    - **Property 5: Intent Classification Completeness**
    - **Validates: Requirements 4.1**

- [ ] 7. RAG 检索服务
  - [ ] 7.1 实现 RAGService
    - 创建 `app/services/rag_service.py`
    - 实现 retrieve(): 查询 ChromaDB，过滤相似度阈值
    - 返回 RAGResult (products, max_similarity, below_threshold)
    - 配置默认阈值 0.7
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 7.2 编写 RAG 检索属性测试
    - **Property 6: RAG Retrieval with Similarity Threshold**
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [ ] 8. Web 搜索服务
  - [ ] 8.1 实现 WebSearchService
    - 创建 `app/services/web_search_service.py`
    - 集成 Tavily API
    - 实现 search(): 返回 SearchResult 列表
    - 实现超时处理和错误处理
    - _Requirements: 7.1, 7.2, 7.4_

- [ ] 9. 上下文组装服务
  - [ ] 9.1 实现 ContextAssembler
    - 创建 `app/services/context_assembler.py`
    - 实现优先级排序: System_Prompt > Current_Query > RAG_Context > User_Profile > Short_Term_Memory
    - 实现 Token 计数和截断逻辑
    - 注入当前系统时间到 System Prompt
    - _Requirements: 6.1, 8.1, 8.4, 8.5_

  - [ ]* 9.2 编写上下文组装属性测试
    - **Property 7: Time Injection in System Prompt**
    - **Property 9: Context Assembly with Token Budget**
    - **Validates: Requirements 6.1, 8.1, 8.4, 8.5**

- [ ] 10. Checkpoint - 核心服务验证
  - 运行所有测试，确保 RAG、意图路由、上下文组装正常
  - 如有问题，询问用户

- [ ] 11. 用户画像提取服务
  - [ ] 11.1 实现 ProfileExtractionAgent
    - 创建 `app/services/profile_agent.py`
    - 实现 extract(): 使用 LLM 分析对话提取结构化画像
    - 实现 update_profile(): 原子事务更新数据库
    - 实现异步触发逻辑 (每 5 条消息)
    - _Requirements: 9.1, 9.2, 9.3, 9.5, 9.6_

  - [ ]* 11.2 编写画像提取属性测试
    - **Property 10: Profile Extraction Lifecycle**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.6**

- [ ] 12. 主聊天服务
  - [ ] 12.1 实现 ChatService
    - 创建 `app/services/chat_service.py`
    - 实现 chat(): 协调意图路由、RAG、Web搜索、上下文组装
    - 实现 SSE 流式响应生成器
    - 实现消息持久化到 SQLite
    - 实现 LLM 重试逻辑 (失败重试一次)
    - _Requirements: 5.4, 7.2, 8.2, 9.4, 12.3_

  - [ ] 12.2 创建聊天路由
    - 创建 `app/routers/chat.py`
    - POST /api/chat (SSE 响应, Content-Type: text/event-stream)
    - GET /api/history (获取对话历史)
    - 实现用户数据隔离 (WHERE user_id = current_user_id)
    - _Requirements: 2.1, 2.4, 2.5, 11.1, 11.4_

  - [ ]* 12.3 编写聊天服务属性测试
    - **Property 3: User Data Isolation**
    - **Property 8: Web Search Context Integration**
    - **Property 11: SSE Streaming Response**
    - **Property 13: LLM Retry on Error**
    - **Validates: Requirements 2.1, 2.3, 2.5, 7.2, 10.4, 11.1, 12.3**

- [ ] 13. 错误处理和中间件
  - [ ] 13.1 实现全局错误处理
    - 创建 `app/core/exceptions.py`，定义自定义异常
    - 创建 `app/core/middleware.py`，实现错误处理中间件
    - 实现标准化错误响应 (error_code, message, request_id)
    - _Requirements: 11.5, 11.6, 12.2, 12.4, 12.5_

  - [ ]* 13.2 编写错误处理属性测试
    - **Property 12: API Error Response Format**
    - **Validates: Requirements 11.5, 11.6**

- [ ] 14. Checkpoint - 后端完整性验证
  - 运行所有后端测试
  - 使用 curl/httpie 手动测试 API 端点
  - 如有问题，询问用户

- [ ] 15. 前端认证页面
  - [ ] 15.1 创建认证组件
    - 创建 `components/auth/LoginForm.tsx`
    - 创建 `components/auth/RegisterForm.tsx`
    - 创建 `app/login/page.tsx` 和 `app/register/page.tsx`
    - 实现表单验证和错误提示
    - _Requirements: 1.2, 1.3_

  - [ ] 15.2 实现认证状态管理
    - 创建 `hooks/useAuth.ts`
    - 实现登录/登出/注册 API 调用
    - 实现认证状态持久化 (Cookie 自动携带)
    - _Requirements: 1.4, 2.2_

- [ ] 16. 前端聊天界面
  - [ ] 16.1 创建布局组件
    - 创建 `components/chat/ChatLayout.tsx`
    - 创建 `components/chat/Sidebar.tsx`
    - 实现响应式布局 (桌面/移动端)
    - _Requirements: 10.1, 10.2, 10.6_

  - [ ] 16.2 创建聊天组件
    - 创建 `components/chat/ChatArea.tsx`
    - 创建 `components/chat/MessageBubble.tsx`
    - 创建 `components/chat/MessageInput.tsx`
    - 实现 Markdown 渲染 (react-markdown + remark-gfm)
    - _Requirements: 10.3, 10.5_

  - [ ] 16.3 实现 SSE 客户端 Hook
    - 创建 `hooks/useSSEChat.ts`
    - 实现流式消息接收和显示
    - 实现自动重连机制 (指数退避)
    - 实现 abort 功能
    - _Requirements: 10.4, 11.1_

  - [ ] 16.4 创建主聊天页面
    - 创建 `app/chat/page.tsx`
    - 集成所有聊天组件
    - 实现对话历史加载和切换
    - _Requirements: 2.1, 10.1, 10.2_

- [ ] 17. 前后端集成
  - [ ] 17.1 配置 API 代理
    - 配置 Next.js rewrites 或 API 代理
    - 处理 CORS 和 Cookie 传递
    - _Requirements: 11.1_

  - [ ] 17.2 实现完整用户流程
    - 注册 → 登录 → 聊天 → 登出
    - 验证用户数据隔离
    - 验证对话历史持久化
    - _Requirements: 2.1, 2.2, 8.3_

- [ ] 18. Final Checkpoint - 端到端验证
  - 运行所有测试 (后端 + 前端)
  - 手动测试完整用户流程
  - 验证多用户隔离
  - 如有问题，询问用户

## Notes

- 任务标记 `*` 为可选测试任务，可跳过以加快 MVP 开发
- 每个 Checkpoint 用于验证阶段性成果，确保增量开发质量
- Property-Based Tests 使用 Hypothesis 库，每个测试至少运行 100 次迭代
- 后端测试使用 pytest-asyncio，前端测试使用 Jest + React Testing Library
