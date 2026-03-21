-- 迁移脚本：为charts表添加image_data字段
-- 用于存储图表图片的base64编码数据

-- PostgreSQL
ALTER TABLE charts ADD COLUMN IF NOT EXISTS image_data TEXT;

-- SQLite (如果使用SQLite)
-- ALTER TABLE charts ADD COLUMN image_data TEXT;

-- 为现有记录初始化image_data字段（可选）
-- UPDATE charts SET image_data = NULL WHERE image_data IS NULL;

-- 创建索引以提高查询性能（可选）
-- CREATE INDEX IF NOT EXISTS idx_charts_created_by ON charts(created_by);
-- CREATE INDEX IF NOT EXISTS idx_charts_created_at ON charts(created_at);
