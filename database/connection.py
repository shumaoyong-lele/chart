#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import json
import os
import secrets
import zlib
import base64
import threading
from datetime import datetime, timedelta
from contextlib import contextmanager
import bcrypt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import get_config
from database.models import Base, UserData, ChartData


class LRUCache:
    def __init__(self, maxsize=128, ttl=300):
        self._cache = {}
        self._timestamps = {}
        self._maxsize = maxsize
        self._ttl = ttl
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            if key in self._cache:
                if datetime.now() - self._timestamps[key] < timedelta(seconds=self._ttl):
                    return self._cache[key]
                del self._cache[key]
                del self._timestamps[key]
        return None

    def set(self, key, value):
        with self._lock:
            if len(self._cache) >= self._maxsize:
                oldest_key = min(self._timestamps, key=self._timestamps.get)
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            self._cache[key] = value
            self._timestamps[key] = datetime.now()

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()


_cache = LRUCache(maxsize=256, ttl=60)


def compress_data(data):
    if data is None:
        return None
    if isinstance(data, (list, dict)):
        data = json.dumps(data)
    compressed = zlib.compress(data.encode('utf-8'))
    return base64.b64encode(compressed).decode('ascii')


def decompress_data(data):
    if data is None:
        return None
    try:
        decoded = base64.b64decode(data.encode('ascii'))
        decompressed = zlib.decompress(decoded)
        return json.loads(decompressed.decode('utf-8'))
    except Exception:
        return data


class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return cls._instance

    def __init__(self, db_url=None):
        if hasattr(self, '_initialized') and self._initialized:
            if db_url is not None and db_url != getattr(self, '_db_url', None):
                raise ValueError("Cannot reinitialize singleton with different db_url")
            return

        self._initialized = True
        self._local = threading.local()

        if db_url is None:
            config = get_config()
            if config and config.get('supabase', {}).get('use_supabase', False):
                db_url = config['supabase']['db_url']
                self.uid = config.get('uid', 'unknown')
            else:
                db_url = 'sqlite:///charts.db'
                self.uid = 'local'

        self._db_url = db_url
        is_sqlite = 'sqlite' in db_url.lower()

        if is_sqlite:
            connect_args = {"check_same_thread": False}
            pool_args = {
                'poolclass': QueuePool,
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_recycle': 3600,
            }
        else:
            connect_args = {"connect_timeout": 10}
            pool_args = {
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
                'pool_recycle': 1800,
                'pool_pre_ping': True,
            }

        self.engine = create_engine(
            db_url,
            echo=False,
            connect_args=connect_args,
            **pool_args
        )

        Base.metadata.create_all(self.engine)

        if is_sqlite:
            self._Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        else:
            self._Session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))

    @property
    def session(self):
        if hasattr(self._local, 'session') and self._local.session is not None:
            return self._local.session
        self._local.session = self._Session()
        return self._local.session

    def close_session(self):
        if hasattr(self._local, 'session') and self._local.session is not None:
            self._local.session.close()
            self._local.session = None

    @contextmanager
    def get_session(self):
        session = self.session
        try:
            yield session
        finally:
            pass

    def _hash_password(self, password):
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise ValueError(f"密码哈希失败: {e}")

    def verify_password(self, password, password_hash):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            raise ValueError(f"密码验证失败: {e}")

    def register_user(self, username, password):
        try:
            existing = self.session.query(UserData).filter_by(username=username).with_for_update().first()
            if existing:
                return {'success': False, 'error': '用户名已存在'}

            try:
                password_hash = self._hash_password(password)
            except ValueError as e:
                return {'success': False, 'error': str(e)}

            uid = str(secrets.randbelow(900000) + 100000)

            user = UserData(
                username=username,
                password_hash=password_hash,
                uid=uid
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

            return {
                'success': True,
                'uid': user.uid,
                'username': user.username,
                'user_id': user.id
            }
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            self.close_session()

    def authenticate_user(self, username, password):
        try:
            cache_key = f"user:{username}"
            cached = _cache.get(cache_key)
            if cached:
                user = cached
            else:
                user = self.session.query(UserData).filter_by(username=username, is_active=True).first()
                if user:
                    _cache.set(cache_key, user)

            if not user:
                return {'success': False, 'error': '用户不存在'}

            try:
                if not self.verify_password(password, user.password_hash):
                    return {'success': False, 'error': '密码错误'}
            except ValueError:
                return {'success': False, 'error': '密码验证失败，请重试'}

            return {
                'success': True,
                'uid': user.uid,
                'username': user.username,
                'user_id': user.id
            }
        finally:
            self.close_session()

    def get_user_by_uid(self, uid):
        try:
            cache_key = f"uid:{uid}"
            cached = _cache.get(cache_key)
            if cached:
                return cached

            user = self.session.query(UserData).filter_by(uid=uid, is_active=True).first()
            if user:
                result = {
                    'id': user.id,
                    'username': user.username,
                    'uid': user.uid,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                _cache.set(cache_key, result)
                return result
            return None
        finally:
            self.close_session()

    def change_password(self, uid, old_password, new_password):
        try:
            user = self.session.query(UserData).filter_by(uid=uid).first()
            if not user:
                return {'success': False, 'error': '用户不存在'}

            try:
                if not self.verify_password(old_password, user.password_hash):
                    return {'success': False, 'error': '原密码错误'}
            except ValueError:
                return {'success': False, 'error': '原密码验证失败，请重试'}

            try:
                user.password_hash = self._hash_password(new_password)
            except ValueError as e:
                return {'success': False, 'error': str(e)}

            self.session.commit()

            _cache.clear()
            return {'success': True, 'message': '密码修改成功'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            self.close_session()

    def save_chart(self, title, chart_type, xdata, ydata, labels=None, created_by=None, image_data=None):
        if created_by is None:
            created_by = self.uid

        try:
            chart = ChartData(
                title=title,
                chart_type=chart_type,
                x_labels=compress_data(xdata),
                y_data=compress_data(ydata),
                labels=compress_data(labels) if labels else None,
                image_data=image_data,
                created_by=created_by
            )
            self.session.add(chart)
            self.session.commit()
            self.session.refresh(chart)

            _cache.clear()
            return chart.id
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.close_session()

    def get_all_charts(self, limit=20, created_by=None):
        try:
            cache_key = f"charts:{created_by}:{limit}"
            if created_by is None:
                cached = _cache.get(cache_key)
                if cached:
                    return cached

            query = self.session.query(ChartData)
            if created_by:
                query = query.filter_by(created_by=created_by)
            charts = query.order_by(ChartData.created_at.desc()).limit(limit).all()

            result = [{
                'id': c.id,
                'title': c.title,
                'chart_type': c.chart_type,
                'x_labels': decompress_data(c.x_labels) if c.x_labels else [],
                'y_data': decompress_data(c.y_data) if c.y_data else [],
                'labels': decompress_data(c.labels) if c.labels else None,
                'image_data': c.image_data if c.image_data else None,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'created_by': c.created_by
            } for c in charts]

            if created_by is None:
                _cache.set(cache_key, result)
            return result
        finally:
            self.close_session()

    def get_chart_by_id(self, chart_id):
        try:
            cache_key = f"chart:{chart_id}"
            cached = _cache.get(cache_key)
            if cached:
                return cached

            chart = self.session.query(ChartData).filter_by(id=chart_id).first()
            if chart:
                result = {
                    'id': chart.id,
                    'title': chart.title,
                    'chart_type': chart.chart_type,
                    'x_labels': decompress_data(chart.x_labels) if chart.x_labels else [],
                    'y_data': decompress_data(chart.y_data) if chart.y_data else [],
                    'labels': decompress_data(chart.labels) if chart.labels else None,
                    'image_data': chart.image_data if chart.image_data else None,
                    'created_at': chart.created_at.isoformat() if chart.created_at else None,
                    'created_by': chart.created_by
                }
                _cache.set(cache_key, result)
                return result
            return None
        finally:
            self.close_session()

    def update_chart(self, chart_id, title=None, xdata=None, ydata=None):
        try:
            chart = self.session.query(ChartData).filter_by(id=chart_id).first()
            if not chart:
                return False
            if title is not None:
                chart.title = title
            if xdata is not None:
                chart.x_labels = compress_data(xdata)
            if ydata is not None:
                chart.y_data = compress_data(ydata)
            self.session.commit()

            _cache.clear()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.close_session()

    def delete_chart(self, chart_id):
        try:
            chart = self.session.query(ChartData).filter_by(id=chart_id).first()
            if chart:
                self.session.delete(chart)
                self.session.commit()
                _cache.clear()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.close_session()

    def search_charts(self, keyword, limit=20):
        try:
            charts = self.session.query(ChartData).filter(
                ChartData.title.contains(keyword)
            ).order_by(ChartData.created_at.desc()).limit(limit).all()

            return [{
                'id': c.id,
                'title': c.title,
                'chart_type': c.chart_type,
                'x_labels': decompress_data(c.x_labels) if c.x_labels else [],
                'y_data': decompress_data(c.y_data) if c.y_data else [],
                'labels': decompress_data(c.labels) if c.labels else None,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'created_by': c.created_by
            } for c in charts]
        finally:
            self.close_session()

    def get_chart_count(self, created_by=None):
        try:
            cache_key = f"count:{created_by}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            query = self.session.query(ChartData.id)
            if created_by:
                query = query.filter_by(created_by=created_by)
            count = query.count()

            _cache.set(cache_key, count)
            return count
        finally:
            self.close_session()

    def batch_save_charts(self, charts_data):
        try:
            charts = []
            for data in charts_data:
                chart = ChartData(
                    title=data['title'],
                    chart_type=data['chart_type'],
                    x_labels=compress_data(data.get('xdata', [])),
                    y_data=compress_data(data.get('ydata', [])),
                    labels=compress_data(data.get('labels')) if data.get('labels') else None,
                    created_by=data.get('created_by', self.uid)
                )
                charts.append(chart)

            self.session.bulk_save_objects(charts)
            self.session.commit()

            _cache.clear()
            return len(charts)
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.close_session()

    def batch_delete_charts(self, chart_ids):
        try:
            self.session.query(ChartData).filter(ChartData.id.in_(chart_ids)).delete(synchronize_session=False)
            self.session.commit()
            _cache.clear()
            return len(chart_ids)
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.close_session()

    def get_recent_charts(self, hours=24, limit=50):
        try:
            cache_key = f"recent:{hours}:{limit}"
            cached = _cache.get(cache_key)
            if cached:
                return cached

            since = datetime.now() - timedelta(hours=hours)
            charts = self.session.query(ChartData).filter(
                ChartData.created_at >= since
            ).order_by(ChartData.created_at.desc()).limit(limit).all()

            result = [{
                'id': c.id,
                'title': c.title,
                'chart_type': c.chart_type,
                'x_labels': decompress_data(c.x_labels) if c.x_labels else [],
                'y_data': decompress_data(c.y_data) if c.y_data else [],
                'labels': decompress_data(c.labels) if c.labels else None,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'created_by': c.created_by
            } for c in charts]

            _cache.set(cache_key, result)
            return result
        finally:
            self.close_session()

    def clear_cache(self):
        _cache.clear()
