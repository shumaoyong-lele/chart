#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class UserData(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    uid = Column(String(20), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_users_username_uid', 'username', 'uid'),
    )


class ChartData(Base):
    __tablename__ = 'charts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    chart_type = Column(String(50), nullable=False)
    x_labels = Column(Text)
    y_data = Column(Text)
    labels = Column(Text)
    image_data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_by = Column(String(100), index=True)

    __table_args__ = (
        Index('idx_charts_created_by_created_at', 'created_by', 'created_at'),
        Index('idx_charts_title_created_at', 'title', 'created_at'),
    )


class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(64), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True))
    ip_address = Column(String(45))


class PasswordResetAttempt(Base):
    __tablename__ = 'password_reset_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, default=False)
