-- 密码重置功能数据库表

-- 1. 密码重置令牌表
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(64) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE INDEX IF NOT EXISTS idx_password_reset_token_hash ON password_reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_password_reset_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_expires_at ON password_reset_tokens(expires_at);

-- 2. 密码重置尝试记录表（用于频率限制）
CREATE TABLE IF NOT EXISTS password_reset_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ip_address VARCHAR(45) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_password_reset_attempt_user_created ON password_reset_attempts(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_password_reset_attempt_ip_created ON password_reset_attempts(ip_address, created_at);

-- 3. 插入测试数据（可选）
-- INSERT INTO password_reset_tokens (user_id, token, token_hash, created_at, expires_at, ip_address)
-- VALUES (1, 'test_token', 'test_hash', NOW(), NOW() + INTERVAL '1 hour', '127.0.0.1');
