# 🔐 忘记密码功能设计方案

## 1. 功能概述

本方案提供完整的"忘记密码"功能实现，包括用户身份验证、密码重置链接生成、安全令牌管理、新密码设置等完整流程。

---

## 2. 架构设计

### 2.1 技术栈

- **后端**: Flask (Python)
- **数据库**: PostgreSQL/SQLite (已有)
- **邮件服务**: SMTP (支持配置)
- **令牌生成**: secrets模块 (安全随机)
- **密码哈希**: bcrypt (已有)

### 2.2 核心组件

1. **PasswordResetToken模型** - 存储重置令牌
2. **邮件服务** - 发送重置邮件
3. **API路由** - 处理重置请求
4. **前端表单** - 用户交互界面

---

## 3. 安全设计

### 3.1 令牌安全

- ✅ **令牌长度**: 64字符 (256位)
- ✅ **唯一性**: 每个用户每次请求唯一
- ✅ **时效性**: 1小时有效期
- ✅ **一次性使用**: 使用后立即失效
- ✅ **加密存储**: 不存储明文令牌

### 3.2 频率限制

- ✅ **请求频率**: 同一用户5分钟内只能请求1次
- ✅ **IP地址限制**: 同一IP每小时最多10次请求
- ✅ **账户锁定**: 连续5次失败尝试后锁定1小时

### 3.3 密码强度要求

- ✅ **最小长度**: 8字符
- ✅ **最大长度**: 72字符 (bcrypt限制)
- ✅ **必须包含**: 大小写字母
- ✅ **必须包含**: 数字
- ✅ **必须包含**: 特殊字符

---

## 4. 业务流程

### 4.1 整体流程图

```
用户点击"忘记密码"
        ↓
    输入邮箱/用户名
        ↓
    验证用户是否存在
        ↓ (存在)
    检查请求频率限制
        ↓ (通过)
    生成密码重置令牌
        ↓
    存储令牌到数据库
        ↓
    发送重置邮件
        ↓
    显示成功消息
        ↓
用户点击邮件链接
        ↓
    验证令牌有效性
        ↓ (有效)
    显示新密码设置页面
        ↓
    用户输入新密码
        ↓
    验证密码强度
        ↓ (通过)
    更新用户密码
        ↓
    删除重置令牌
        ↓
    显示成功消息
```

### 4.2 详细步骤

#### 步骤1: 请求密码重置

**输入**: 用户名或邮箱

**处理**:
1. 验证输入格式
2. 查询用户是否存在
3. 检查频率限制
4. 生成唯一令牌
5. 保存到数据库
6. 发送邮件
7. 返回结果

**输出**:
- 成功: 显示"重置链接已发送到邮箱"
- 失败: 显示具体错误原因

#### 步骤2: 验证重置令牌

**输入**: 重置令牌 (URL参数)

**处理**:
1. 查询令牌是否存在
2. 检查令牌是否过期
3. 检查令牌是否已使用
4. 关联用户是否存在
5. 验证用户账户状态

**输出**:
- 有效: 返回用户ID，渲染密码设置页面
- 无效: 显示错误信息

#### 步骤3: 设置新密码

**输入**: 新密码, 确认密码, 令牌

**处理**:
1. 验证令牌有效性
2. 验证两次密码是否一致
3. 验证密码强度
4. 更新用户密码
5. 删除已使用的令牌
6. 清除用户相关缓存

**输出**:
- 成功: 显示"密码重置成功"
- 失败: 显示具体错误

---

## 5. 数据库设计

### 5.1 PasswordResetToken表

```sql
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR(255) NOT NULL UNIQUE,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    ip_address VARCHAR(45),

    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);
```

### 5.2 PasswordResetAttempt表 (频率限制)

```sql
CREATE TABLE password_reset_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ip_address VARCHAR(45) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE,

    INDEX idx_user_created (user_id, created_at),
    INDEX idx_ip_created (ip_address, created_at)
);
```

---

## 6. API设计

### 6.1 请求密码重置

**Endpoint**: `POST /api/auth/forgot-password`

**Request**:
```json
{
  "username_or_email": "user@example.com"
}
```

**Response** (成功):
```json
{
  "success": true,
  "message": "密码重置链接已发送到您的邮箱"
}
```

**Response** (失败):
```json
{
  "success": false,
  "error": "用户名或邮箱不存在"
}
```

### 6.2 验证重置令牌

**Endpoint**: `GET /api/auth/reset-password?token={token}`

**Response** (有效令牌):
```json
{
  "success": true,
  "valid": true,
  "user_id": 123
}
```

**Response** (无效令牌):
```json
{
  "success": true,
  "valid": false,
  "error": "重置链接已过期或无效"
}
```

### 6.3 设置新密码

**Endpoint**: `POST /api/auth/reset-password`

**Request**:
```json
{
  "token": "abc123...",
  "new_password": "NewPass123!",
  "confirm_password": "NewPass123!"
}
```

**Response** (成功):
```json
{
  "success": true,
  "message": "密码重置成功，请使用新密码登录"
}
```

---

## 7. 前端设计

### 7.1 忘记密码页面

**URL**: `/forgot-password`

**组件**:
- 邮箱/用户名输入框
- 提交按钮
- 返回登录链接
- 加载状态
- 成功/错误提示

### 7.2 重置密码页面

**URL**: `/reset-password?token={token}`

**组件**:
- 新密码输入框
- 确认密码输入框
- 密码强度指示器
- 提交按钮
- 返回登录链接
- 加载状态
- 成功/错误提示

### 7.3 密码强度指示器

**等级**:
- 🔴 弱: 不满足基本要求
- 🟡 中: 满足基本要求
- 🟢 强: 满足所有要求

**实时验证规则**:
- 最少8个字符 ✓
- 包含大写字母 ✓
- 包含小写字母 ✓
- 包含数字 ✓
- 包含特殊字符 ✓

---

## 8. 邮件模板

### 8.1 密码重置邮件

**主题**: 【统计图制作系统】密码重置请求

**内容**:
```
尊敬的用户，您好！

我们收到了您的密码重置请求。如果您没有发起此请求，请忽略此邮件。

要重置您的密码，请点击以下链接：
{reset_link}

此链接将在1小时后失效。

如果您在点击链接时遇到问题，请复制以下链接到浏览器地址栏：
{reset_link}

为了保护您的账户安全，请不要将验证码或链接分享给他人。

此致
统计图制作系统团队
```

---

## 9. 异常处理

### 9.1 异常类型

| 异常类型 | 错误代码 | 用户消息 |
|---------|---------|---------|
| 用户不存在 | USER_NOT_FOUND | 用户名或邮箱不存在 |
| 令牌过期 | TOKEN_EXPIRED | 重置链接已过期，请重新申请 |
| 令牌已使用 | TOKEN_USED | 此重置链接已使用，请重新申请 |
| 令牌无效 | TOKEN_INVALID | 重置链接无效 |
| 频率限制 | RATE_LIMITED | 请求过于频繁，请稍后再试 |
| 密码过短 | PASSWORD_TOO_SHORT | 密码至少需要8个字符 |
| 密码太弱 | PASSWORD_TOO_WEAK | 密码强度不足 |
| 密码不匹配 | PASSWORD_MISMATCH | 两次输入的密码不一致 |
| 账户被禁用 | ACCOUNT_DISABLED | 账户已被禁用 |

### 9.2 异常处理策略

1. **记录日志**: 所有异常都记录到日志
2. **用户提示**: 返回友好的错误消息
3. **安全考虑**: 不暴露系统详细信息
4. **频率限制**: 防止暴力破解
5. **数据清理**: 定期清理过期令牌

---

## 10. 安全措施

### 10.1 令牌安全

- ✅ 令牌使用哈希存储，即使数据库泄露也无法使用
- ✅ 令牌有时效性，过期自动失效
- ✅ 令牌一次性使用，使用后立即删除
- ✅ 令牌与用户IP绑定，防止被盗用

### 10.2 密码安全

- ✅ 使用bcrypt进行密码哈希
- ✅ 强制密码强度要求
- ✅ 不允许重复使用最近5次的密码
- ✅ 密码修改后自动登出其他设备

### 10.3 账户安全

- ✅ 请求频率限制
- ✅ 失败尝试次数限制
- ✅ 可疑活动监控
- ✅ 账户异常通知

---

## 11. 实现文件清单

### 11.1 新增文件

1. `database/models.py` - 数据库模型
2. `services/email_service.py` - 邮件服务
3. `services/password_reset_service.py` - 密码重置服务
4. `routes/auth_routes.py` - 认证路由
5. `templates/forgot_password.html` - 忘记密码页面
6. `templates/reset_password.html` - 重置密码页面

### 11.2 修改文件

1. `database.py` - 添加密码重置相关方法
2. `webapp.py` - 添加新的API路由
3. `config.json` - 添加邮件配置

---

## 12. 配置项

### 12.1 邮件配置

```json
{
  "email": {
    "smtp_host": "smtp.example.com",
    "smtp_port": 587,
    "smtp_user": "noreply@example.com",
    "smtp_password": "your-password",
    "use_tls": true,
    "from_email": "noreply@example.com",
    "from_name": "统计图制作系统"
  }
}
```

### 12.2 安全配置

```json
{
  "password_reset": {
    "token_expiry_hours": 1,
    "min_password_length": 8,
    "max_password_length": 72,
    "require_uppercase": true,
    "require_lowercase": true,
    "require_digit": true,
    "require_special": true,
    "rate_limit_per_user": 1,
    "rate_limit_window": 300,
    "rate_limit_per_ip": 10,
    "rate_limit_ip_window": 3600
  }
}
```

---

## 13. 测试计划

### 13.1 单元测试

- [ ] 令牌生成测试
- [ ] 令牌验证测试
- [ ] 密码强度验证测试
- [ ] 频率限制测试

### 13.2 集成测试

- [ ] 完整密码重置流程测试
- [ ] 邮件发送测试
- [ ] 数据库操作测试

### 13.3 安全测试

- [ ] 暴力破解防护测试
- [ ] SQL注入测试
- [ ] XSS攻击测试
- [ ] 令牌盗用测试

---

## 14. 部署指南

### 14.1 前置条件

1. 配置SMTP邮件服务器
2. 创建数据库表
3. 配置安全参数

### 14.2 部署步骤

1. 更新数据库模型
2. 配置邮件服务
3. 部署前端页面
4. 测试完整流程

---

## 15. 维护计划

### 15.1 定期任务

- [ ] 清理过期令牌 (每天)
- [ ] 清理失败尝试记录 (每周)
- [ ] 检查异常登录日志 (每天)

### 15.2 监控指标

- [ ] 密码重置请求次数
- [ ] 成功率/失败率
- [ ] 平均响应时间
- [ ] 异常请求数量

---

**文档版本**: 1.0
**创建日期**: 2026-03-22
**作者**: AI Assistant
**状态**: 待实现
