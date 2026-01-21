import uiautomator2 as u2
import random
import time
import logging
from typing import Dict, List, Optional

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局设备状态
_devices_pool:  Dict[str, u2.Device] = {}
_status:  Dict[str, dict] = {}
_stop_flag: Dict[str, bool] = {}

# ==================== 设备管理 ====================

def get_devices() -> List[Dict]:
    """获取已连接的ADB设备列表"""
    try:
        devices = u2.adb. device_list()
        device_list = []
        for device in devices:
            # 尝试连接并获取设备信息
            try:
                d = u2.connect(device)
                info = d.info
                device_list.append({
                    "id": device,
                    "name": f"{info.get('model', 'Unknown')}({device})",
                    "status":  "online"
                })
            except: 
                device_list.append({
                    "id": device,
                    "name": device,
                    "status": "offline"
                })
        return device_list
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        return []

def switch_device(device_id: str) -> bool:
    """切换到指定设备"""
    try:
        if device_id in _devices_pool:
            del _devices_pool[device_id]
        
        d = u2.connect(device_id)
        _devices_pool[device_id] = d
        _status[device_id] = {
            "is_running": False,
            "remain_time": 0,
            "visited":  0,
            "current_keyword": "",
            "connection_status": "online"
        }
        _stop_flag[device_id] = False
        logger.info(f"已连接设备: {device_id}")
        return True
    except Exception as e:
        logger. error(f"连接设备失败: {e}")
        return False

def device_status(device_id: str) -> dict:
    """获取设备状态"""
    return _status.get(device_id, {
        "is_running": False,
        "remain_time": 0,
        "visited": 0,
        "connection_status": "offline"
    })

def stop_yanghao(device_id:  str):
    """停止养号"""
    _stop_flag[device_id] = True
    logger.info(f"已请求停止设备 {device_id} 的养号")

# ==================== 默认配置 ====================

def get_default_config() -> dict:
    """获取默认配置"""
    return {
        "keywords": ["科技资讯", "旅行攻略", "美食教程"],
        "duration_minutes": 20,
        "post_visit_ratio": 50,
        "max_posts_per_run": 10,
        "visit_control": {
            "filter_image_text": True,
            "duration_range": [25, 45],
            "slide_interval": [3, 5],
            "slide_distance":  "single_image"
        },
        "interaction": {
            "like_prob": 15,
            "collect_prob": 10,
            "comment_prob": 5,
            "comment_templates": [
                "不错的分享！",
                "学习了~",
                "感谢分享",
                "很有用的内容",
                "已收藏学习"
            ]
        }
    }

# ==================== 养号主流程 ====================

def run_yanghao(device_id: str, config: dict):
    """执行养号流程"""
    try:
        if device_id not in _devices_pool:
            logger.error(f"设备 {device_id} 未连接")
            return
        
        d = _devices_pool[device_id]
        total_time = config['duration_minutes'] * 60
        visited = 0
        max_posts = config['max_posts_per_run']
        
        _status[device_id] = {
            "is_running": True,
            "remain_time":  config['duration_minutes'],
            "visited": 0,
            "connection_status": "online"
        }
        
        logger.info(f"开始养号 - 设备: {device_id}, 时长: {config['duration_minutes']}分钟")
        
        t0 = time.time()
        
        while time.time() - t0 < total_time and visited < max_posts:
            if _stop_flag. get(device_id, False):
                logger.info(f"养号已停止 - 设备: {device_id}")
                break
            
            # 随机选择关键词
            keywords = config. get('keywords', [])
            if not keywords:
                logger.warning("关键词列表为空")
                break
            
            keyword = random.choice(keywords)
            _status[device_id]["current_keyword"] = keyword
            
            # 打开小红书搜索框
            logger.info(f"搜索关键词: {keyword}")
            _search_and_visit_posts(d, keyword, config, device_id, total_time - (time.time() - t0))
            
            visited = _status[device_id]['visited']
            remain_time = int((total_time - (time.time() - t0)) / 60)
            _status[device_id]["remain_time"] = max(0, remain_time)
            
            # 长随机间隔（避免频繁操作）
            wait_time = random.randint(30, 60)
            logger.info(f"等待 {wait_time} 秒后继续")
            time.sleep(wait_time)
        
        # 养号完成
        logger.info(f"养号完成 - 设备: {device_id}, 访问帖子数: {visited}")
        _status[device_id] = {
            "is_running": False,
            "remain_time": 0,
            "visited": visited,
            "connection_status":  "online"
        }
        _stop_flag[device_id] = False
        
    except Exception as e:
        logger.error(f"养号异常 - 设备: {device_id}, 错误: {e}")
        _status[device_id]["is_running"] = False

def _search_and_visit_posts(d:  u2.Device, keyword: str, config: dict, device_id: str, remain_time: float):
    """搜索并访问帖子"""
    try: 
        # 1. 打开搜索框 (需根据实际UI调整)
        # 假设存在搜索按钮或搜索框
        d.press("home")  # 回到首页
        time.sleep(random.randint(2, 4))
        
        # 点击搜索框 - 示例选择器（需根据实际APP调整）
        search_box = d(resourceId="com.xingin.xhs: id/search_bar", focusable=True)
        if search_box. exists:
            search_box. click()
            time.sleep(random.randint(1, 2))
        else:
            logger.warning("搜索框未找到")
            return
        
        # 2. 输入关键词
        d. send_keys(keyword)
        time.sleep(random.randint(1, 2))
        
        # 按搜索按钮或回车
        d.press("enter")
        time.sleep(random.randint(2, 4))
        
        # 3. 滚动并访问帖子
        post_visit_ratio = config['post_visit_ratio'] / 100.0
        max_posts = config['max_posts_per_run']
        duration_range = config['visit_control']['duration_range']
        
        visited_count = 0
        scroll_count = 0
        max_scrolls = int(max_posts / post_visit_ratio) + 5
        
        while visited_count < max_posts and scroll_count < max_scrolls:
            if _stop_flag.get(device_id, False):
                break
            
            # 随机决定是否访问本帖子
            if random.random() < post_visit_ratio:
                # 点击第一个可见的帖子
                posts = d(className="android.view.View")
                if posts.exists:
                    post_item = posts[0] if len(posts) > 0 else None
                    if post_item:
                        try:
                            post_item.click()
                            time.sleep(random.randint(2, 3))
                            
                            # 4. 访问帖子详情
                            _visit_post_detail(d, config, device_id, duration_range)
                            visited_count += 1
                            _status[device_id]["visited"] = visited_count
                            
                            # 返回列表
                            d.press("back")
                            time.sleep(random.randint(2, 3))
                        except Exception as e:
                            logger.error(f"访问帖子失败: {e}")
                            d.press("back")
            
            # 滑动到下一个帖子
            d.swipe(500, 1000, 500, 300, duration=0.5)  # 上滑
            time.sleep(random.randint(1, 3))
            scroll_count += 1
    
    except Exception as e: 
        logger.error(f"搜索访问失败: {e}")

def _visit_post_detail(d: u2.Device, config: dict, device_id: str, duration_range: List[int]):
    """访问帖子详情并执行互动"""
    try:
        # 随机访问时长
        visit_duration = random.randint(duration_range[0], duration_range[1])
        logger.info(f"访问帖子详情，预计停留 {visit_duration} 秒")
        
        visit_start = time.time()
        slide_interval = config['visit_control']['slide_interval']
        
        # 5. 模拟浏览：随机滑动图片
        while time.time() - visit_start < visit_duration:
            if _stop_flag.get(device_id, False):
                break
            
            # 每隔3-5秒滑动一次
            wait_before_slide = random.randint(slide_interval[0], slide_interval[1])
            time.sleep(min(wait_before_slide, visit_duration - (time.time() - visit_start)))
            
            if time.time() - visit_start < visit_duration:
                # 上滑图片
                d.swipe(500, 1000, 500, 300, duration=0.3)
                time.sleep(random.randint(1, 2))
        
        # 6. 执行互动行为
        interaction_cfg = config['interaction']
        
        # 点赞
        if random.randint(1, 100) <= interaction_cfg['like_prob']:
            _do_like(d)
        
        # 收藏
        if random.randint(1, 100) <= interaction_cfg['collect_prob']: 
            _do_collect(d)
        
        # 评论
        if random.randint(1, 100) <= interaction_cfg['comment_prob']: 
            comments = interaction_cfg['comment_templates']
            comment_text = random.choice(comments)
            _do_comment(d, comment_text)
        
    except Exception as e:
        logger.error(f"访问帖子详情失败: {e}")

def _do_like(d: u2.Device):
    """执行点赞"""
    try:
        like_btn = d(resourceId="com.xingin.xhs:id/like_btn", clickable=True)
        if like_btn.exists:
            like_btn.click()
            logger.info("已点赞")
            time.sleep(random.randint(1, 2))
    except Exception as e: 
        logger.error(f"点赞失败: {e}")

def _do_collect(d: u2.Device):
    """执行收藏"""
    try:
        collect_btn = d(resourceId="com.xingin.xhs:id/collect_btn", clickable=True)
        if collect_btn.exists:
            collect_btn.click()
            logger.info("已收藏")
            time.sleep(random.randint(1, 2))
    except Exception as e:
        logger.error(f"收藏失败: {e}")

def _do_comment(d: u2.Device, comment_text: str):
    """执行评论"""
    try:
        comment_btn = d(resourceId="com.xingin.xhs:id/comment_btn", clickable=True)
        if comment_btn.exists:
            comment_btn.click()
            time.sleep(random.randint(1, 2))
            
            comment_input = d(resourceId="com. xingin.xhs:id/comment_input_field")
            if comment_input.exists:
                comment_input.set_text(comment_text)
                time.sleep(random.randint(1, 2))
                
                send_btn = d(resourceId="com.xingin.xhs:id/comment_send_btn", clickable=True)
                if send_btn.exists:
                    send_btn.click()
                    logger.info(f"已评论: {comment_text}")
                    time.sleep(random.randint(1, 2))
    except Exception as e:
        logger.error(f"评论失败: {e}")