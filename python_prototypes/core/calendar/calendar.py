#!/usr/bin/env python3
"""
游戏时间系统核心模块

主要功能:
- 基础时间管理: 360天/年历法系统
- 纪元锚定: anchor_era() - 指定纪元元年对应的公元年份
- 改元功能: start_new_era() - 从当前年份开始新纪元
- 时间推进: 支持小时/天级别的时间流逝
- 日历格式化: 公历和纪年两种显示方式

核心设计:
- 纯锚定系统: 只使用锚定机制，不再维护纪元节点列表
- 改元=锚定当前年: start_new_era()内部调用anchor_era(name, current_year)
- 未来限制: 不允许锚定到未来年份
- 实时计算: 纪元年份基于锚定实时计算

最后更新: 2025-06-12 - 简化为纯锚定系统
"""

from typing import Optional, Tuple
from enum import Enum

from ..config import EPOCH_START_YEAR, HOURS_PER_DAY, DAYS_PER_YEAR


class TimeUnit(Enum):
    """时间单位枚举"""
    HOUR = "hour"
    DAY = "day"


class Calendar:
    """日历显示器 - 负责时间的格式化显示和时间管理

    专为回合制游戏设计的时间系统，支持非匀速时间流逝、精确时间控制和纪年管理。

    Attributes:
        DAYS_PER_YEAR (int): 每年天数，默认360天
        HOURS_PER_DAY (int): 每天小时数，默认24小时
        BASE_YEAR (int): 起始年份，默认公元前722年

    Example:
        >>> calendar = Calendar()
        >>> calendar.advance_time(30, TimeUnit.DAY)
        >>> print(f"当前年份: {calendar.current_year}")
        >>> calendar.start_new_era("开元")
        >>> calendar.anchor_era("开元", 713)  # 开元元年=公元713年
    """

    HOURS_PER_DAY = HOURS_PER_DAY
    DAYS_PER_YEAR = DAYS_PER_YEAR

    def __init__(self, base_year: int = -2000):
        self.base_year = base_year
        # 当前时间（以小时为最小单位）
        self._timestamp_hour = 0

        # 当前锚定：(纪元名, 元年公元年份)
        self._current_anchor: Optional[Tuple[str, int]] = ('uninitialized', self.base_year)

    @property
    def current_gregorian_year(self) -> int:
        """当前年份（公元年）"""
        total_days = self._timestamp_hour // self.HOURS_PER_DAY
        return self.base_year + (total_days // self.DAYS_PER_YEAR)


    def anchor_era(self, era_name: str, gregorian_year: int) -> None:
        """锚定纪元

        指定某个纪元的元年对应的公元年份，用于纪元显示计算。
        不允许锚定到比当前时间还晚的时期。

        Args:
            era_name: 纪元名称，如"开元"
            gregorian_year: 纪元元年对应的公元年份，如713（开元元年=公元713年）

        Raises:
            ValueError: 当锚定年份晚于当前年份时

        Example:
            >>> calendar.anchor_era("开元", 713)  # 开元元年=公元713年
        """
        if not era_name.strip():
            raise ValueError("era_name cannot be empty or whitespace")

        current_year = self.current_gregorian_year
        if gregorian_year > current_year:
            raise ValueError(f"不能锚定到未来时期：锚定年份{gregorian_year}晚于当前年份{current_year}")

        # 存储为 (纪元名, 元年公元年份)
        self._current_anchor = (era_name, gregorian_year)

    def start_new_era(self, name: str) -> None:
        """改元 - 开始新纪元

        从当前年份开始新的纪元。

        Args:
            name: 新纪元名称，如"永徽"、"开元"等

        Raises:
            ValueError: 当纪元名称为空时

        Example:
            >>> calendar.start_new_era("永徽")  # 从当前年份开始永徽纪元
        """
        if not name.strip():
            raise ValueError("name cannot be empty or whitespace")

        # 改元就是锚定当前年份为新纪元的元年
        self.anchor_era(name, self.current_gregorian_year)


    def get_timestamp(self) -> int:
        """获取当前时间戳（小时数）

        Returns:
            int: 从起始时间开始的总小时数
        """
        return self._timestamp_hour

    def advance_time_tick(self) -> None:
        """推进时间一个tick（1小时）"""
        self._timestamp_hour += 1

    def get_time_info(self) -> dict:
        """获取当前时间信息"""
        total_days = self._timestamp_hour // self.HOURS_PER_DAY
        day_in_year = (total_days % self.DAYS_PER_YEAR) + 1
        hour_in_day = self._timestamp_hour % self.HOURS_PER_DAY
        month = ((day_in_year - 1) // 30) + 1
        day_in_month = ((day_in_year - 1) % 30) + 1
        
        # 获取纪元信息
        era_name = None
        era_year = None
        if self._current_anchor:
            anchor_era_name, gregorian_year = self._current_anchor
            current_year = self.current_gregorian_year
            if current_year >= gregorian_year:
                era_name = anchor_era_name
                era_year = current_year - gregorian_year + 1
        
        return {
            'timestamp': self._timestamp_hour,
            'gregorian_year': self.current_gregorian_year,
            'month': month,
            'day_in_month': day_in_month,
            'day_in_year': day_in_year,
            'hour_in_day': hour_in_day,
            'current_era_name': era_name,
            'current_era_year': era_year,
            'current_anchor': self._current_anchor
        }

    def reset(self) -> None:
        """重置时间到起始状态"""
        self._timestamp_hour = 0
        self._current_anchor = ('uninitialized', self.base_year)

    def format_date_gregorian(self, show_hour: bool = False) -> str:
        """格式化为公历日期显示

        Args:
            show_hour: 是否显示小时

        Returns:
            格式化的日期字符串
        """
        year = self.current_gregorian_year
        total_days = self._timestamp_hour // self.HOURS_PER_DAY
        day_in_year = (total_days % self.DAYS_PER_YEAR) + 1
        month = ((day_in_year - 1) // 30) + 1
        day = ((day_in_year - 1) % 30) + 1
        hour = self._timestamp_hour % self.HOURS_PER_DAY

        # 处理公元前年份
        if year < 0:
            year_str = f"公元前{abs(year)}年"
        else:
            year_str = f"公元{year}年"

        if show_hour:
            return f"{year_str}{month}月{day}日{hour}点"
        else:
            return f"{year_str}{month}月{day}日"

    def format_date_era(self, show_hour: bool = False) -> str:
        """格式化为纪年日期显示

        Args:
            show_hour: 是否显示小时

        Returns:
            格式化的日期字符串
        """
        # 获取纪元信息
        era_name = None
        era_year = None
        if self._current_anchor:
            anchor_era_name, gregorian_year = self._current_anchor
            current_year = self.current_gregorian_year
            if current_year >= gregorian_year:
                era_name = anchor_era_name
                era_year = current_year - gregorian_year + 1
        
        if era_name is None or era_year is None:
            return self.format_date_gregorian(show_hour)

        total_days = self._timestamp_hour // self.HOURS_PER_DAY
        day_in_year = (total_days % self.DAYS_PER_YEAR) + 1
        month = ((day_in_year - 1) // 30) + 1
        day = ((day_in_year - 1) % 30) + 1
        hour = self._timestamp_hour % self.HOURS_PER_DAY

        if show_hour:
            return f"{era_name}{era_year}年{month}月{day}日{hour}点"
        else:
            return f"{era_name}{era_year}年{month}月{day}日"

    def get_time_status_text(self) -> str:
        """获取详细的时间状态文本"""
        info = self.get_time_info()
        gregorian = self.format_date_gregorian(True)
        era = self.format_date_era(True)

        status_lines = [
            f"公历: {gregorian}",
            f"纪年: {era}",
            f"年内第{info['day_in_year']}天",
            f"总计: {info['timestamp']}小时"
        ]

        # 显示锚定信息
        if info['current_anchor']:
            era_name, gregorian_year = info['current_anchor']
            status_lines.append(f"锚定: {era_name}元年 = 公元{gregorian_year}年")

        return "\n".join(status_lines)