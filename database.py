from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import json

# 尝试导入配置文件
try:
    from config import SUPABASE_DB_URL, USE_SUPABASE
except ImportError:
    # 默认配置
    SUPABASE_DB_URL = None
    USE_SUPABASE = False

Base = declarative_base()


class ChartData(Base):
    """图表数据模型"""
    __tablename__ = 'charts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    chart_type = Column(String(50), nullable=False)  # line, bar, pie, multi_line
    x_labels = Column(Text)  # JSON 格式
    y_data = Column(Text)    # JSON 格式
    labels = Column(Text)    # 折线图标签（JSON 格式）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_url=None):
        """
        初始化数据库连接

        Args:
            db_url: Supabase PostgreSQL 连接字符串
                   格式: postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
        """
        if db_url is None:
            # 如果配置文件中指定使用 Supabase，则使用 Supabase
            if USE_SUPABASE and SUPABASE_DB_URL:
                db_url = SUPABASE_DB_URL
            else:
                # 默认使用本地 SQLite（开发用）
                db_url = 'sqlite:///charts.db'

        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_chart(self, title, chart_type, xdata, ydata, labels=None, created_by="user"):
        """
        保存图表数据到数据库

        Args:
            title: 图表标题
            chart_type: 图表类型 (line, bar, pie, multi_line)
            xdata: x轴数据列表
            ydata: y轴数据列表
            labels: 折线图标签列表（复式折线图用）
            created_by: 创建者

        Returns:
            int: 保存的记录 ID
        """
        session = self.Session()
        try:
            chart = ChartData(
                title=title,
                chart_type=chart_type,
                x_labels=json.dumps(xdata),
                y_data=json.dumps(ydata),
                labels=json.dumps(labels) if labels else None,
                created_by=created_by
            )
            session.add(chart)
            session.commit()
            session.refresh(chart)
            print(f"✅ 图表已保存到数据库 (ID: {chart.id})")
            return chart.id
        except Exception as e:
            session.rollback()
            print(f"❌ 保存失败: {e}")
            return None
        finally:
            session.close()

    def get_all_charts(self, limit=20):
        """
        获取所有图表记录

        Args:
            limit: 返回数量限制

        Returns:
            list: 图表记录列表
        """
        session = self.Session()
        try:
            charts = session.query(ChartData).order_by(
                ChartData.created_at.desc()
            ).limit(limit).all()

            result = []
            for chart in charts:
                result.append({
                    'id': chart.id,
                    'title': chart.title,
                    'chart_type': chart.chart_type,
                    'x_labels': json.loads(chart.x_labels) if chart.x_labels else [],
                    'y_data': json.loads(chart.y_data) if chart.y_data else [],
                    'labels': json.loads(chart.labels) if chart.labels else None,
                    'created_at': chart.created_at,
                    'created_by': chart.created_by
                })
            return result
        finally:
            session.close()

    def get_chart_by_id(self, chart_id):
        """
        根据 ID 获取图表

        Args:
            chart_id: 图表 ID

        Returns:
            dict or None
        """
        session = self.Session()
        try:
            chart = session.query(ChartData).filter_by(id=chart_id).first()
            if chart:
                return {
                    'id': chart.id,
                    'title': chart.title,
                    'chart_type': chart.chart_type,
                    'x_labels': json.loads(chart.x_labels) if chart.x_labels else [],
                    'y_data': json.loads(chart.y_data) if chart.y_data else [],
                    'labels': json.loads(chart.labels) if chart.labels else None,
                    'created_at': chart.created_at,
                    'created_by': chart.created_by
                }
            return None
        finally:
            session.close()

    def delete_chart(self, chart_id):
        """
        删除图表记录

        Args:
            chart_id: 图表 ID

        Returns:
            bool: 是否成功
        """
        session = self.Session()
        try:
            chart = session.query(ChartData).filter_by(id=chart_id).first()
            if chart:
                session.delete(chart)
                session.commit()
                print(f"✅ 图表 {chart_id} 已删除")
                return True
            print(f"❌ 未找到 ID 为 {chart_id} 的图表")
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ 删除失败: {e}")
            return False
        finally:
            session.close()


# 全局数据库实例
db = DatabaseManager()
