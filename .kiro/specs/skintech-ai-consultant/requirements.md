# Requirements Document

## Introduction

SkinTech AI Consultant 是一个基于 Web 的智能美妆聊天应用。该应用具备用户管理功能、本地 RAG（检索增强生成）知识库、长短期记忆管理以及时间感知能力。核心是一个具有"配方师"人设的 AI Agent，能够根据用户肤质和偏好提供个性化的美妆护肤建议。

## Glossary

- **System**: SkinTech AI Consultant 应用系统
- **User**: 使用该应用的终端用户
- **Agent**: 具有"配方师"人设的 AI 聊天助手
- **RAG**: Retrieval-Augmented Generation，检索增强生成
- **Vector_Database**: 存储产品 Embedding 的向量数据库 (ChromaDB)
- **SQLite_Database**: 存储用户信息和对话历史的关系型数据库
- **Short_Term_Memory**: 最近 10 轮对话记录
- **Long_Term_Memory**: 用户肤质和偏好的总结性信息
- **User_Profile**: 存储用户长期偏好和特征的结构化数据
- **Session**: 用户的一次对话会话
- **Intent_Router**: 意图分类器，决定查询路由
- **Profile_Extraction_Agent**: 异步提取用户画像的后台 Agent
- **Similarity_Threshold**: 向量检索的相似度阈值（默认 0.7）

## Requirements

### Requirement 1: User Authentication

**User Story:** As a user, I want to register, login, and logout of the system, so that I can have a secure and personalized experience.

#### Acceptance Criteria

1. WHEN a new user submits registration with username and password, THE System SHALL hash the password using bcrypt and create a new user account
2. WHEN a user submits valid login credentials, THE System SHALL verify the hashed password and return a valid JWT token
3. WHEN a user submits invalid login credentials, THE System SHALL reject the authentication and return an error message without revealing which field is incorrect
4. WHILE a user is authenticated, THE System SHALL include the user's token in all subsequent API requests
5. IF a user's token expires or is invalid, THEN THE System SHALL return 401 and require re-authentication
6. WHEN a user requests logout, THE System SHALL invalidate the current session token

### Requirement 2: User Data Isolation

**User Story:** As a user, I want my conversation history to be private and isolated, so that other users cannot see my personal skincare discussions.

#### Acceptance Criteria

1. WHEN a user logs in, THE System SHALL load only that user's conversation history
2. WHEN a user switches accounts, THE System SHALL clear the previous user's data from the interface and load the new user's history
3. THE System SHALL associate all chat messages with the authenticated user's ID
4. Every database query (SELECT/INSERT/UPDATE) SHALL include a WHERE user_id = current_user_id clause enforced at the Service layer
5. IF a request attempts to access another user's data, THEN THE System SHALL return 403 Forbidden

### Requirement 3: Product Data Generation

**User Story:** As a system administrator, I want to generate and prepare mock skincare product data, so that the RAG system has a standardized knowledge base to query.

#### Acceptance Criteria

1. WHEN the data generation script is executed, THE System SHALL generate approximately 5000 mock skincare product records
2. THE System SHALL include the following fields for each product: product_name, brand, core_ingredients, suitable_skin_types, efficacy, risk_ingredients, price_range
3. WHEN product data is generated, THE System SHALL save it to a JSON file (products_data.json)
4. BEFORE vectorization, THE System SHALL format each product into a standardized template: "Product: [Name], Brand: [Brand], Contains: [Ingredients], Good for: [SkinType], Effects: [Efficacy], Caution: [RiskIngredients], Price: [PriceRange]"
5. WHEN the ingestion script is executed, THE System SHALL vectorize the formatted product data and store embeddings in ChromaDB

### Requirement 4: Intent Classification and Routing

**User Story:** As a user, I want my queries to be intelligently routed, so that I get the most appropriate response source.

#### Acceptance Criteria

1. WHEN a user sends a message, THE Intent_Router SHALL classify the query into one of: PRODUCT_KNOWLEDGE, GENERAL_CHAT, EXTERNAL_KNOWLEDGE
2. WHEN intent is PRODUCT_KNOWLEDGE, THE System SHALL proceed to RAG retrieval
3. WHEN intent is GENERAL_CHAT, THE System SHALL respond directly without RAG retrieval
4. WHEN intent is EXTERNAL_KNOWLEDGE (e.g., "2025年最新防晒"), THE System SHALL trigger web search
5. THE Intent_Router SHALL use keyword analysis or a lightweight classifier for intent detection

### Requirement 5: RAG-Based Chat with Similarity Threshold

**User Story:** As a user, I want to ask skincare questions and receive answers based on the product knowledge base with quality filtering.

#### Acceptance Criteria

1. WHEN querying ChromaDB, THE System SHALL retrieve documents with a cosine similarity score above the Similarity_Threshold (default 0.7, configurable)
2. WHEN documents meet the threshold, THE System SHALL include the top 3 most relevant products as context
3. IF no documents meet the Similarity_Threshold, THEN THE System SHALL execute the Web Search Fallback flow
4. WHEN constructing the LLM prompt, THE System SHALL include the retrieved product information as context
5. THE Agent SHALL respond with the persona of a professional "配方师" (formulator/cosmetic chemist)

### Requirement 6: Time-Aware Responses

**User Story:** As a user, I want the AI to understand time context in my questions, so that it can provide advice based on how long I've been using products.

#### Acceptance Criteria

1. WHEN calling the LLM, THE System SHALL inject the current system time in format "Current System Time: {YYYY-MM-DD HH:MM:SS}" into the system prompt
2. WHEN a user references relative time (e.g., "上周", "三天前"), THE Agent SHALL calculate the actual date based on current time and conversation history timestamps
3. WHEN providing skincare advice, THE Agent SHALL consider the duration of product usage from historical context

### Requirement 7: Web Search Fallback

**User Story:** As a user, I want the AI to search the web when it doesn't have information in its knowledge base, so that I can get up-to-date information.

#### Acceptance Criteria

1. WHEN Intent_Router classifies as EXTERNAL_KNOWLEDGE OR RAG retrieval returns no results above threshold, THE System SHALL trigger web search using Tavily or DuckDuckGo
2. WHEN web search is triggered, THE System SHALL integrate search results into the response context
3. WHEN presenting web search results, THE Agent SHALL clearly indicate the information source with citations
4. IF web search fails or times out, THEN THE Agent SHALL acknowledge the limitation and suggest the user search manually

### Requirement 8: Short-Term Memory and Token Budget Management

**User Story:** As a user, I want the AI to remember our recent conversation, so that I don't have to repeat context.

#### Acceptance Criteria

1. WHEN constructing the LLM prompt, THE System SHALL include the most recent 10 conversation turns
2. THE System SHALL persist all conversation messages to SQLite_Database immediately after each exchange
3. WHEN the server restarts, THE System SHALL restore conversation history from SQLite_Database
4. THE System SHALL prioritize context assembly in the following order: System_Prompt (highest) > Current_Query > RAG_Context > User_Profile > Short_Term_Memory (lowest)
5. IF total tokens exceed the model limit, THE System SHALL remove oldest messages from Short_Term_Memory FIRST while preserving higher priority components

### Requirement 9: Long-Term Memory and User Profile

**User Story:** As a user, I want the AI to remember my skin type and preferences over time, so that recommendations become more personalized.

#### Acceptance Criteria

1. THE System SHALL trigger Profile_Extraction_Agent asynchronously after every 5 user messages OR at the end of a session
2. THE Profile_Extraction_Agent SHALL analyze conversation history and extract structured user preferences (skin_type, sensitivities, preferred_brands, budget_range)
3. THE System SHALL store the extracted profile in the User_Profile field in SQLite_Database
4. WHEN constructing the LLM prompt, THE System SHALL inject the User_Profile summary as context
5. THE Profile_Extraction_Agent SHALL run in background without blocking the main chat response
6. THE System SHALL handle database concurrency using atomic transactions when updating User_Profile to prevent race conditions

### Requirement 10: Chat User Interface

**User Story:** As a user, I want a modern chat interface similar to ChatGPT, so that I can easily interact with the AI consultant.

#### Acceptance Criteria

1. THE System SHALL display a sidebar on the left for conversation history and settings
2. THE System SHALL display the main chat area on the right for the current conversation
3. WHEN a user sends a message, THE System SHALL display it immediately in the chat area
4. WHEN the AI responds, THE System SHALL stream the response token by token to the chat area
5. THE System SHALL render Markdown content in chat bubbles (including headers, lists, bold, and code blocks)
6. THE System SHALL be responsive and work on both desktop and mobile devices

### Requirement 11: API Endpoints

**User Story:** As a frontend developer, I want well-defined API endpoints, so that I can integrate the frontend with the backend.

#### Acceptance Criteria

1. THE System SHALL use Server-Sent Events (SSE) for the POST /api/chat endpoint to stream responses with Content-Type: text/event-stream
2. THE System SHALL expose POST /api/auth/login and POST /api/auth/register endpoints for authentication
3. THE System SHALL expose POST /api/auth/logout endpoint for session invalidation
4. THE System SHALL expose a GET /api/history endpoint for retrieving conversation history
5. WHEN an API request lacks valid authentication, THE System SHALL return a 401 Unauthorized response
6. THE System SHALL return standardized error responses with error_code, message, and request_id fields

### Requirement 12: Non-Functional Requirements

**User Story:** As a user, I want the system to be fast, reliable, and handle errors gracefully.

#### Acceptance Criteria

1. THE System SHALL achieve Time to First Token (TTFT) of less than 2 seconds for chat responses
2. IF the LLM API times out (>30 seconds), THEN THE System SHALL return a friendly error message and suggest retry
3. IF the LLM API returns an error, THEN THE System SHALL retry once before returning an error to the user
4. THE System SHALL log all errors with request_id for debugging
5. WHEN ChromaDB or SQLite is unavailable, THE System SHALL return a service unavailable message rather than crashing
