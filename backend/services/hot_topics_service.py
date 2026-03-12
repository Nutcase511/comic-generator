"""
热门话题服务
每天第一次启动时搜索热门话题并缓存
"""
import sys
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 缓存文件路径
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hot_topics_cache.json")
# 缓存有效期（小时）
CACHE_VALID_HOURS = 24


class HotTopicsService:
    """热门话题服务"""

    def __init__(self):
        self.cache_dir = os.path.dirname(CACHE_FILE)
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)

    def _load_cache(self) -> Dict:
        """加载缓存数据"""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
        return {}

    def _save_cache(self, data: Dict):
        """保存缓存数据"""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        cache = self._load_cache()
        if not cache:
            return False

        try:
            cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
            expiry_time = cache_time + timedelta(hours=CACHE_VALID_HOURS)
            return datetime.now() < expiry_time
        except Exception as e:
            logger.error(f"检查缓存有效性失败: {e}")
            return False

    def _format_topic_name(self, title: str) -> str:
        """格式化话题名称"""
        # 移除一些常见的无用后缀
        name = title
        for suffix in [' - 搜索', ' - 百度', ' - 微博', ' - 知乎', ' 相关搜索']:
            name = name.replace(suffix, '')

        # 限制长度
        if len(name) > 15:
            name = name[:15] + '...'

        return name.strip()

    async def fetch_hot_topics(self) -> List[Dict]:
        """
        获取热门话题
        如果缓存有效则返回缓存，否则重新搜索

        Returns:
            热门话题列表
        """
        # 检查缓存是否有效
        if self._is_cache_valid():
            cache = self._load_cache()
            logger.info("使用缓存的热门话题")
            return cache.get('topics', [])

        # 缓存无效，重新搜索
        logger.info("缓存过期或不存在，开始搜索热门话题")
        topics = await self._search_hot_topics()

        # 保存到缓存
        if topics:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'topics': topics
            }
            self._save_cache(cache_data)
            logger.info(f"成功获取并缓存 {len(topics)} 个热门话题")

        return topics

    async def _search_hot_topics(self) -> List[Dict]:
        """
        搜索热门话题

        Returns:
            热门话题列表
        """
        try:
            # 这里我们搜索多个来源的热门话题
            search_queries = [
                "今日热点 2026",
                "微博热搜 今日",
                "知乎热榜 今日",
                "百度热搜榜 今日",
                "今日头条热点"
            ]

            all_topics = []

            # 搜索每个查询
            for query in search_queries:
                try:
                    topics = await self._search_query(query)
                    all_topics.extend(topics)
                except Exception as e:
                    logger.warning(f"搜索 '{query}' 失败: {e}")
                    continue

            # 去重并取前5个
            unique_topics = self._deduplicate_topics(all_topics)
            return unique_topics[:5]

        except Exception as e:
            logger.error(f"搜索热门话题失败: {e}")
            # 返回默认话题
            return self._get_default_topics()

    async def _search_query(self, query: str) -> List[Dict]:
        """
        执行单个搜索查询

        Args:
            query: 搜索查询

        Returns:
            话题列表
        """
        try:
            # 使用搜索API来获取热门话题
            # 这里返回基于当前时间的热门话题模拟数据
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month
            day = current_date.day

            # 根据搜索查询返回相关的热门话题
            if "微博" in query:
                return [
                    {
                        "id": f"weibo_{year}{month}{day}_1",
                        "title": f"{year}年{month}月社会热点",
                        "description": "今日微博热搜榜热门话题"
                    },
                    {
                        "id": f"weibo_{year}{month}{day}_2",
                        "title": "科技圈最新动态",
                        "description": "科技领域热门讨论"
                    }
                ]
            elif "知乎" in query:
                return [
                    {
                        "id": f"zhihu_{year}{month}{day}_1",
                        "title": "职场生存指南",
                        "description": "知乎热榜职场话题"
                    },
                    {
                        "id": f"zhihu_{year}{month}{day}_2",
                        "title": "教育改革讨论",
                        "description": "教育领域热门话题"
                    }
                ]
            elif "百度" in query:
                return [
                    {
                        "id": f"baidu_{year}{month}{day}_1",
                        "title": "娱乐新闻汇总",
                        "description": "百度热搜娱乐话题"
                    },
                    {
                        "id": f"baidu_{year}{month}{day}_2",
                        "title": "健康生活趋势",
                        "description": "健康领域热门话题"
                    }
                ]
            else:
                return [
                    {
                        "id": f"general_{year}{month}{day}_1",
                        "title": "今日综合热点",
                        "description": f"{year}年{month}月{day}日热点汇总"
                    }
                ]

        except Exception as e:
            logger.error(f"执行搜索查询失败: {e}")
            return []

    def _deduplicate_topics(self, topics: List[Dict]) -> List[Dict]:
        """
        去重话题

        Args:
            topics: 话题列表

        Returns:
            去重后的话题列表
        """
        seen = set()
        unique = []

        for topic in topics:
            # 使用标题作为唯一标识
            title = topic.get('title', '')
            if title and title not in seen:
                seen.add(title)
                unique.append(topic)

        return unique

    def _get_default_topics(self) -> List[Dict]:
        """获取默认话题（当搜索失败时使用）"""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.weekday()  # 0=周一, 6=周日

        # 根据星期几生成不同的话题组合
        weekday_topics = {
            0: [  # 周一
                {"id": f"work_monday_{year}", "title": "周一综合症", "description": "工作日开始的困扰"},
                {"id": f"work_plan_{year}", "title": "工作计划", "description": "一周工作规划"},
            ],
            1: [  # 周二
                {"id": f"productivity_{year}", "title": "工作效率", "description": "提升工作生产力"},
                {"id": f"team_collab_{year}", "title": "团队协作", "description": "职场合作技巧"},
            ],
            2: [  # 周三
                {"id": f"mid_week_{year}", "title": "周中状态", "description": "工作周中期的调整"},
                {"id": f"project_manage_{year}", "title": "项目管理", "description": "工作项目管理"},
            ],
            3: [  # 周四
                {"id": f"tech_update_{year}", "title": "科技前沿", "description": "最新科技动态"},
                {"id": f"innovation_{year}", "title": "创新思维", "description": "工作创新方法"},
            ],
            4: [  # 周五
                {"id": f"weekend_prep_{year}", "title": "周末准备", "description": "周末生活规划"},
                {"id": f"work_balance_{year}", "title": "工作生活平衡", "description": "职场与生活"},
            ],
        }

        # 基础话题
        base_topics = [
            {
                "id": f"ai_develop_{year}",
                "title": "人工智能发展",
                "description": "AI技术的最新进展和应用"
            },
            {
                "id": f"remote_work_{year}",
                "title": "远程办公趋势",
                "description": "居家办公的未来发展"
            },
            {
                "id": f"social_anxiety_{year}",
                "title": "社交媒体焦虑",
                "description": "网络社交带来的心理问题"
            },
        ]

        # 添加星期特定话题
        if day in weekday_topics:
            base_topics.extend(weekday_topics[day])

        # 添加季节性话题
        season = (month - 1) // 3  # 0=春, 1=夏, 2=秋, 3=冬
        season_topics = {
            0: [
                {"id": f"spring_plan_{year}", "title": "春季规划", "description": "新年计划实施"},
                {"id": f"career_growth_{year}", "title": "职业发展", "description": "春季职场机会"},
            ],
            1: [
                {"id": f"summer_life_{year}", "title": "夏日生活", "description": "夏季生活方式"},
                {"id": f"vacation_mode_{year}", "title": "假期模式", "description": "夏日度假计划"},
            ],
            2: [
                {"id": f"autumn_review_{year}", "title": "秋季复盘", "description": "年度总结准备"},
                {"id": f"harvest_time_{year}", "title": "收获季节", "description": "成果总结"},
            ],
            3: [
                {"id": f"winter_warmth_{year}", "title": "冬日温暖", "description": "冬季生活温馨"},
                {"id": f"year_end_{year}", "title": "年终总结", "description": "年度回顾"},
            ],
        }

        base_topics.extend(season_topics.get(season, []))

        # 取前5个
        return base_topics[:5]


# 创建全局实例
hot_topics_service = HotTopicsService()
