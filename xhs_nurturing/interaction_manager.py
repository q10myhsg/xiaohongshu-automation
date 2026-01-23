import random
import logging
from typing import List, Optional
import uiautomator2 as u2
from .utils import random_delay, safe_click, simulate_typing

class InteractionManager:
    """互动管理器"""
    
    def __init__(self):
        """初始化互动管理器"""
        self.logger = logging.getLogger(__name__)
    
    def do_interaction(self, device: u2.Device, config: dict):
        """
        执行互动行为
        :param device: 设备实例
        :param config: 配置字典
        """
        interaction_cfg = config.get('interaction', {})
        
        # 点赞
        if random.randint(1, 100) <= interaction_cfg.get('like_prob', 15):
            self.do_like(device)
        
        # 收藏
        if random.randint(1, 100) <= interaction_cfg.get('collect_prob', 10):
            self.do_collect(device)
        
        # 评论
        if random.randint(1, 100) <= interaction_cfg.get('comment_prob', 5):
            comments = interaction_cfg.get('comment_templates', [])
            self.do_comment(device, comments)
    
    def do_like(self, device: u2.Device) -> bool:
        """
        执行点赞
        :param device: 设备实例
        :return: 是否点赞成功
        """
        try:
            # 尝试多种可能的点赞按钮选择器
            like_selectors = [
                device(resourceId="com.xingin.xhs:id/like_btn", clickable=True),
                device(resourceId="com.xingin.xhs:id/like_button", clickable=True),
                device(description="点赞", clickable=True),
                device(text="点赞", clickable=True)
            ]
            
            for selector in like_selectors:
                if selector.exists:
                    if safe_click(device, selector):
                        self.logger.info("已点赞")
                        random_delay(1, 2)
                        return True
            
            self.logger.warning("未找到点赞按钮")
            return False
        except Exception as e:
            self.logger.error(f"点赞失败: {e}")
            return False
    
    def do_collect(self, device: u2.Device) -> bool:
        """
        执行收藏
        :param device: 设备实例
        :return: 是否收藏成功
        """
        try:
            # 尝试多种可能的收藏按钮选择器
            collect_selectors = [
                device(resourceId="com.xingin.xhs:id/collect_btn", clickable=True),
                device(resourceId="com.xingin.xhs:id/collect_button", clickable=True),
                device(description="收藏", clickable=True),
                device(text="收藏", clickable=True)
            ]
            
            for selector in collect_selectors:
                if selector.exists:
                    if safe_click(device, selector):
                        self.logger.info("已收藏")
                        random_delay(1, 2)
                        return True
            
            self.logger.warning("未找到收藏按钮")
            return False
        except Exception as e:
            self.logger.error(f"收藏失败: {e}")
            return False
    
    def do_comment(self, device: u2.Device, comment_templates: List[str]) -> bool:
        """
        执行评论
        :param device: 设备实例
        :param comment_templates: 评论模板列表
        :return: 是否评论成功
        """
        try:
            if not comment_templates:
                self.logger.warning("评论模板列表为空")
                return False
            
            # 尝试多种可能的评论按钮选择器
            comment_btn_selectors = [
                device(resourceId="com.xingin.xhs:id/comment_btn", clickable=True),
                device(resourceId="com.xingin.xhs:id/comment_button", clickable=True),
                device(description="评论", clickable=True),
                device(text="评论", clickable=True)
            ]
            
            # 点击评论按钮
            comment_btn_found = False
            for selector in comment_btn_selectors:
                if selector.exists:
                    if safe_click(device, selector):
                        comment_btn_found = True
                        break
            
            if not comment_btn_found:
                self.logger.warning("未找到评论按钮")
                return False
            
            random_delay(1, 2)
            
            # 尝试多种可能的评论输入框选择器
            comment_input_selectors = [
                device(resourceId="com.xingin.xhs:id/comment_input_field"),
                device(resourceId="com.xingin.xhs:id/comment_input"),
                device(className="android.widget.EditText", focusable=True),
                device(description="写评论...")
            ]
            
            # 输入评论内容
            comment_input_found = False
            for selector in comment_input_selectors:
                if selector.exists:
                    # 随机选择一条评论模板
                    comment_text = random.choice(comment_templates)
                    simulate_typing(selector, comment_text)
                    self.logger.debug(f"输入评论: {comment_text}")
                    comment_input_found = True
                    break
            
            if not comment_input_found:
                self.logger.warning("未找到评论输入框")
                device.press("back")
                return False
            
            random_delay(1, 2)
            
            # 尝试多种可能的发送按钮选择器
            send_btn_selectors = [
                device(resourceId="com.xingin.xhs:id/comment_send_btn", clickable=True),
                device(resourceId="com.xingin.xhs:id/send_button", clickable=True),
                device(text="发送", clickable=True),
                device(description="发送", clickable=True)
            ]
            
            # 点击发送按钮
            send_btn_found = False
            for selector in send_btn_selectors:
                if selector.exists:
                    if safe_click(device, selector):
                        send_btn_found = True
                        break
            
            if not send_btn_found:
                self.logger.warning("未找到发送按钮")
                device.press("back")
                return False
            
            self.logger.info(f"已评论: {comment_text}")
            random_delay(1, 2)
            return True
        except Exception as e:
            self.logger.error(f"评论失败: {e}")
            try:
                device.press("back")
            except:
                pass
            return False
    
    def do_follow(self, device: u2.Device) -> bool:
        """
        执行关注
        :param device: 设备实例
        :return: 是否关注成功
        """
        try:
            # 尝试多种可能的关注按钮选择器
            follow_selectors = [
                device(resourceId="com.xingin.xhs:id/follow_btn", clickable=True),
                device(resourceId="com.xingin.xhs:id/follow_button", clickable=True),
                device(text="关注", clickable=True),
                device(description="关注", clickable=True)
            ]
            
            for selector in follow_selectors:
                if selector.exists:
                    if safe_click(device, selector):
                        self.logger.info("已关注")
                        random_delay(1, 2)
                        return True
            
            self.logger.warning("未找到关注按钮")
            return False
        except Exception as e:
            self.logger.error(f"关注失败: {e}")
            return False
    
    def do_share(self, device: u2.Device) -> bool:
        """
        执行分享
        :param device: 设备实例
        :return: 是否分享成功
        """
        try:
            # 尝试多种可能的分享按钮选择器
            share_selectors = [
                device(resourceId="com.xingin.xhs:id/share_btn", clickable=True),
                device(resourceId="com.xingin.xhs:id/share_button", clickable=True),
                device(text="分享", clickable=True),
                device(description="分享", clickable=True)
            ]
            
            for selector in share_selectors:
                if selector.exists:
                    if safe_click(device, selector):
                        self.logger.info("已打开分享面板")
                        random_delay(1, 2)
                        # 关闭分享面板
                        device.press("back")
                        random_delay(1, 2)
                        return True
            
            self.logger.warning("未找到分享按钮")
            return False
        except Exception as e:
            self.logger.error(f"分享失败: {e}")
            try:
                device.press("back")
            except:
                pass
            return False
    
    def _find_image_container(self, device):
        """
        查找图片容器
        :param device: 设备实例
        :return: 图片容器或None
        """
        try:
            frame_layouts = device(className="android.widget.FrameLayout")
            for fl in frame_layouts:
                try:
                    content_desc = fl.info.get('contentDescription', '')
                    if '图片' in content_desc:
                        return fl
                except Exception as e:
                    self.logger.debug(f"获取FrameLayout信息失败: {e}")
                    continue
            return None
        except Exception as e:
            self.logger.error(f"查找图片容器失败: {e}")
            return None
    
    def _extract_image_count(self, image_container):
        """
        提取图片数量
        :param image_container: 图片容器
        :return: 图片数量
        """
        try:
            content_desc = image_container.info.get('contentDescription', '')
            self.logger.info(f"图片容器contentDescription: {content_desc}")
            
            import re
            match = re.search(r'共(\d+)张', content_desc)
            if match:
                total_images = int(match.group(1))
                self.logger.info(f"识别到图片数量: {total_images}张")
                return total_images
            else:
                self.logger.warning("无法识别图片数量")
                return 1
        except Exception as e:
            self.logger.error(f"提取图片数量失败: {e}")
            return 1
    
    def _swipe_through_images(self, device, total_images):
        """
        滑动浏览图片
        :param device: 设备实例
        :param total_images: 图片数量
        """
        try:
            # 最多滑动浏览10张图片
            max_possible_swipe = min(total_images - 1, 10)
            
            # 随机选择要浏览的图片数量
            if max_possible_swipe > 0:
                num_images_to_view = random.randint(1, max_possible_swipe)
                self.logger.info(f"随机选择浏览 {num_images_to_view} 张图片")
                
                for i in range(num_images_to_view):
                    # 从右向左滑动（查看下一张）
                    screen_width, screen_height = self._get_screen_size(device)
                    if screen_width and screen_height:
                        start_x = screen_width * random.uniform(0.7, 0.9)
                        end_x = screen_width * random.uniform(0.1, 0.3)
                        y = screen_height * random.uniform(0.4, 0.6)
                        device.swipe(start_x, y, end_x, y, duration=0.1)
                        self.logger.info(f"向左滑动浏览第{i+2}张图片")
                        random_delay(1, 10)
            else:
                self.logger.info("只有1张图片，无需滑动")
        except Exception as e:
            self.logger.error(f"滑动浏览图片失败: {e}")
    
    def _get_screen_size(self, device):
        """
        获取屏幕尺寸
        :param device: 设备实例
        :return: (width, height)
        """
        try:
            device_info = device.info
            if device_info:
                screen_width = device_info.get('displayWidth', 1080)
                screen_height = device_info.get('displayHeight', 1920)
                return screen_width, screen_height
            return 1080, 1920
        except Exception as e:
            self.logger.error(f"获取屏幕尺寸失败: {e}")
            return 1080, 1920
    
    def view_image_note_with_interaction(self, device, config):
        """
        浏览图片笔记并执行互动操作
        :param device: 设备实例
        :param config: 配置字典
        :return: 是否为图片笔记
        """
        try:
            # 查找图片容器
            image_container = self._find_image_container(device)
            if not image_container:
                self.logger.info("当前笔记不是图片笔记")
                random_delay(0.1, 0.5)
                return False
            
            # 获取图片边界
            image_bounds = image_container.info.get('bounds', {})
            if not image_bounds:
                self.logger.warning("无法获取图片边界信息")
                return False
            
            # 计算图片中心位置
            image_width = image_bounds['right'] - image_bounds['left']
            image_height = image_bounds['bottom'] - image_bounds['top']
            center_x = image_bounds['left'] + image_width / 2
            center_y = image_bounds['top'] + image_height / 2
            
            # 提取图片数量
            total_images = self._extract_image_count(image_container)
            
            # 滑动浏览图片
            self._swipe_through_images(device, total_images)
            
            # 浏览完图片后，向上滚动查看评论
            self.logger.info("向上滚动查看评论")
            self._scroll_randomly(device)
            random_delay(1, 2)
            
            # 执行互动操作
            self.do_like(device)
            self.do_collect(device)
            
            # 执行评论
            interaction_cfg = config.get('interaction', {})
            comment_templates = interaction_cfg.get('comment_templates', [])
            if comment_templates:
                self.do_comment(device, comment_templates)
            
            return True
        except Exception as e:
            self.logger.error(f"浏览图片笔记失败: {e}")
            return False
    
    def _scroll_randomly(self, device):
        """
        随机滚动
        :param device: 设备实例
        """
        try:
            screen_width, screen_height = self._get_screen_size(device)
            if screen_width and screen_height:
                # 随机选择滚动方向
                if random.choice([True, False]):
                    # 向上滚动
                    start_y = screen_height * random.uniform(0.7, 0.9)
                    end_y = screen_height * random.uniform(0.1, 0.3)
                    x = screen_width * random.uniform(0.4, 0.6)
                    device.swipe(x, start_y, x, end_y, duration=0.2)
                else:
                    # 向下滚动
                    start_y = screen_height * random.uniform(0.1, 0.3)
                    end_y = screen_height * random.uniform(0.7, 0.9)
                    x = screen_width * random.uniform(0.4, 0.6)
                    device.swipe(x, start_y, x, end_y, duration=0.2)
        except Exception as e:
            self.logger.error(f"随机滚动失败: {e}")