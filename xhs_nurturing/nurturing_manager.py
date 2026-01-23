import time
import logging
import random
from typing import Dict, Optional
import uiautomator2 as u2
from .device_manager import DeviceManager
from .config_manager import ConfigManager
from .interaction_manager import InteractionManager
from .browse_manager import BrowseManager
from .utils import random_delay, validate_keywords

class NurturingManager:
    """养号管理器"""
    
    def __init__(self):
        """初始化养号管理器"""
        self.device_manager = DeviceManager()
        self.config_manager = ConfigManager()
        self.interaction_manager = InteractionManager()
        self.browse_manager = BrowseManager()
        self.logger = logging.getLogger(__name__)
        self._running_tasks = set()
    
    def start_nurturing(self, device_id: str) -> bool:
        """
        开始养号
        :param device_id: 设备ID
        :return: 是否成功开始
        """
        try:
            if device_id in self._running_tasks:
                self.logger.warning(f"设备 {device_id} 已经在养号中")
                return False
            
            # 连接设备
            if not self.device_manager.connect_device(device_id):
                self.logger.error(f"无法连接设备 {device_id}")
                return False
            
            # 获取设备配置
            config = self.config_manager.get_device_config(device_id)
            
            # 验证配置
            if not self.config_manager.validate_config(config):
                self.logger.error(f"设备 {device_id} 的配置无效")
                return False
            
            # 验证关键词
            if not validate_keywords(config.get("keywords", [])):
                self.logger.error(f"设备 {device_id} 的关键词配置无效")
                return False
            
            # 更新设备状态
            self.device_manager.update_device_status(
                device_id,
                is_running=True,
                remain_time=config["duration_minutes"],
                visited=0,
                current_keyword=""
            )
            
            # 添加到运行任务
            self._running_tasks.add(device_id)
            
            # 执行养号流程
            self.logger.info(f"开始养号 - 设备: {device_id}, 时长: {config['duration_minutes']}分钟")
            
            # 异步执行养号流程
            import threading
            thread = threading.Thread(target=self._run_nurturing, args=(device_id, config))
            thread.daemon = True
            thread.start()
            
            return True
        except Exception as e:
            self.logger.error(f"开始养号失败: {e}")
            return False
    
    def _run_nurturing(self, device_id: str, config: Dict):
        """
        执行养号流程
        :param device_id: 设备ID
        :param config: 配置字典
        """
        try:
            total_time = config['duration_minutes'] * 60
            max_posts_per_keyword = config.get('posts_per_keyword', 10)
            discovery_browse_time = config.get('discovery_browse_time', 10)
            
            t0 = time.time()
            
            # 获取设备
            device = self.device_manager.get_device(device_id)
            if not device:
                self.logger.error(f"无法获取设备 {device_id}")
                return
            
            # 1. 启动小红书
            self.logger.info(f"启动小红书 - 设备: {device_id}")
            if not self.browse_manager.start_xiaohongshu(device):
                self.logger.error(f"启动小红书失败 - 设备: {device_id}")
                return
            
            # 在发现页浏览一段时间
            self.logger.info(f"在发现页浏览 {discovery_browse_time} 秒 - 设备: {device_id}")
            self.browse_manager.browse_discovery_page(device, discovery_browse_time, config)
            
            # 随机选择关键词
            keywords = config.get('keywords', [])
            if not keywords:
                self.logger.warning("关键词列表为空")
                return
            
            for keyword in keywords:
                if time.time() - t0 >= total_time:
                    break
                
                if self.device_manager.is_stop_requested(device_id):
                    self.logger.info(f"养号已停止 - 设备: {device_id}")
                    break
                
                self.device_manager.update_device_status(device_id, current_keyword=keyword)
                self.logger.info(f"开始处理关键词: {keyword} - 设备: {device_id}")
                
                # 3. 点击搜索
                # 4. 输入关键词
                # 5. 搜索关键词并浏览帖子
                self.browse_manager.search_and_browse(
                    device, 
                    keyword, 
                    config, 
                    max_posts=max_posts_per_keyword
                )
                
                # 更新状态
                visited = self.device_manager.device_status(device_id).get('visited', 0)
                remain_time = int((total_time - (time.time() - t0)) / 60)
                self.device_manager.update_device_status(device_id, remain_time=max(0, remain_time))
                
                # 长随机间隔（避免频繁操作）
                wait_time = random.randint(30, 60)
                self.logger.info(f"等待 {wait_time} 秒后继续 - 设备: {device_id}")
                time.sleep(wait_time)
            
            # 养号完成
            final_status = self.device_manager.device_status(device_id)
            final_visited = final_status.get('visited', 0)
            self.logger.info(f"养号完成 - 设备: {device_id}, 访问帖子数: {final_visited}")
            
            # 更新设备状态
            self.device_manager.update_device_status(
                device_id,
                is_running=False,
                remain_time=0,
                visited=final_visited,
                current_keyword=""
            )
            
        except Exception as e:
            self.logger.error(f"养号异常 - 设备: {device_id}, 错误: {e}")
            # 更新设备状态
            self.device_manager.update_device_status(device_id, is_running=False)
        finally:
            # 从运行任务中移除
            if device_id in self._running_tasks:
                self._running_tasks.remove(device_id)
    
    def stop_nurturing(self, device_id: str):
        """
        停止养号
        :param device_id: 设备ID
        """
        self.device_manager.stop_task(device_id)
        self.logger.info(f"已请求停止设备 {device_id} 的养号")
    
    def get_device_status(self, device_id: str) -> dict:
        """
        获取设备状态
        :param device_id: 设备ID
        :return: 设备状态
        """
        return self.device_manager.device_status(device_id)
    
    def get_all_devices(self) -> list:
        """
        获取所有设备
        :return: 设备列表
        """
        return self.device_manager.get_devices()
    
    def get_running_devices(self) -> list:
        """
        获取正在运行养号的设备
        :return: 设备ID列表
        """
        return list(self._running_tasks)
    
    def update_device_config(self, device_id: str, config: Dict) -> bool:
        """
        更新设备配置
        :param device_id: 设备ID
        :param config: 配置字典
        :return: 是否成功
        """
        try:
            # 验证配置
            if not self.config_manager.validate_config(config):
                self.logger.error(f"设备 {device_id} 的配置无效")
                return False
            
            # 保存配置
            self.config_manager.set_device_config(device_id, config)
            self.logger.info(f"已更新设备 {device_id} 的配置")
            return True
        except Exception as e:
            self.logger.error(f"更新设备配置失败: {e}")
            return False
    
    def update_keywords(self, device_id: str, keywords: list) -> bool:
        """
        更新设备关键词
        :param device_id: 设备ID
        :param keywords: 关键词列表
        :return: 是否成功
        """
        try:
            # 验证关键词
            if not validate_keywords(keywords):
                self.logger.error(f"设备 {device_id} 的关键词配置无效")
                return False
            
            # 保存关键词
            self.config_manager.set_keywords(device_id, keywords)
            self.logger.info(f"已更新设备 {device_id} 的关键词列表")
            return True
        except Exception as e:
            self.logger.error(f"更新设备关键词失败: {e}")
            return False
    
    def update_comment_templates(self, device_id: str, comment_templates: list) -> bool:
        """
        更新设备评论模板
        :param device_id: 设备ID
        :param comment_templates: 评论模板列表
        :return: 是否成功
        """
        try:
            # 验证评论模板
            if not isinstance(comment_templates, list):
                self.logger.error(f"设备 {device_id} 的评论模板必须是列表")
                return False
            
            # 保存评论模板
            self.config_manager.set_comment_templates(device_id, comment_templates)
            self.logger.info(f"已更新设备 {device_id} 的评论模板列表")
            return True
        except Exception as e:
            self.logger.error(f"更新设备评论模板失败: {e}")
            return False
    
    def get_device_config(self, device_id: str) -> Dict:
        """
        获取设备配置
        :param device_id: 设备ID
        :return: 设备配置
        """
        return self.config_manager.get_device_config(device_id)
    
    def is_device_running(self, device_id: str) -> bool:
        """
        检查设备是否正在养号
        :param device_id: 设备ID
        :return: 是否正在养号
        """
        return device_id in self._running_tasks
    
    def cleanup(self):
        """
        清理资源
        """
        try:
            # 停止所有养号任务
            for device_id in list(self._running_tasks):
                self.stop_nurturing(device_id)
            
            # 断开所有设备连接
            for device_id in self.device_manager.get_connected_devices():
                self.device_manager.disconnect_device(device_id)
            
            self.logger.info("已清理所有资源")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")