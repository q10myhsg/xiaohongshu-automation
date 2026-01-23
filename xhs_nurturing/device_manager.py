import uiautomator2 as u2
import subprocess
import logging
from typing import Dict, List, Optional
from datetime import datetime

class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        """初始化设备管理器"""
        self._devices_pool: Dict[str, u2.Device] = {}
        self._status: Dict[str, dict] = {}
        self._stop_flag: Dict[str, bool] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_devices(self) -> List[Dict]:
        """
        获取已连接的ADB设备列表
        :return: 设备列表，每个设备包含id、name和status
        """
        try:
            # 使用subprocess调用adb命令获取设备列表
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            self.logger.info(f"adb devices输出: {result.stdout}")
            lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
            
            device_list = []
            self.logger.info(f"设备行数: {len(lines)}")
            
            for line in lines:
                self.logger.info(f"处理设备行: {line}")
                if line.strip():
                    parts = line.split('\t')
                    self.logger.info(f"分割结果: {parts}")
                    if len(parts) >= 2:
                        device_id = parts[0]
                        status = parts[1]
                        self.logger.info(f"设备ID: {device_id}, 状态: {status}")
                        
                        # 尝试连接并获取设备信息
                        try:
                            self.logger.info(f"尝试连接设备: {device_id}")
                            d = u2.connect(device_id)
                            info = d.info
                            self.logger.info(f"设备信息: {info}")
                            device_list.append({
                                "id": device_id,
                                "name": f"{info.get('model', 'Unknown')}({device_id})",
                                "status": "online"
                            })
                        except Exception as e:
                            self.logger.error(f"连接设备失败: {e}")
                            device_list.append({
                                "id": device_id,
                                "name": device_id,
                                "status": "offline"
                            })
            
            self.logger.info(f"最终设备列表: {device_list}")
            return device_list
        except Exception as e:
            self.logger.error(f"获取设备列表失败: {e}")
            return []
    
    def connect_device(self, device_id: str) -> bool:
        """
        连接指定设备
        :param device_id: 设备ID
        :return: 是否连接成功
        """
        try:
            if device_id in self._devices_pool:
                del self._devices_pool[device_id]
            
            d = u2.connect(device_id)
            self._devices_pool[device_id] = d
            self._status[device_id] = {
                "is_running": False,
                "remain_time": 0,
                "visited": 0,
                "current_keyword": "",
                "connection_status": "online",
                "last_connected": datetime.now().isoformat()
            }
            self._stop_flag[device_id] = False
            self.logger.info(f"已连接设备: {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"连接设备失败: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[u2.Device]:
        """
        获取设备连接
        :param device_id: 设备ID
        :return: 设备连接实例，若未连接返回None
        """
        return self._devices_pool.get(device_id)
    
    def device_status(self, device_id: str) -> dict:
        """
        获取设备状态
        :param device_id: 设备ID
        :return: 设备状态
        """
        return self._status.get(device_id, {
            "is_running": False,
            "remain_time": 0,
            "visited": 0,
            "connection_status": "offline"
        })
    
    def update_device_status(self, device_id: str, **kwargs):
        """
        更新设备状态
        :param device_id: 设备ID
        :param kwargs: 状态键值对
        """
        if device_id not in self._status:
            self._status[device_id] = {
                "is_running": False,
                "remain_time": 0,
                "visited": 0,
                "connection_status": "offline"
            }
        self._status[device_id].update(kwargs)
    
    def stop_task(self, device_id: str):
        """
        停止设备上的任务
        :param device_id: 设备ID
        """
        self._stop_flag[device_id] = True
        self.logger.info(f"已请求停止设备 {device_id} 的任务")
    
    def is_stop_requested(self, device_id: str) -> bool:
        """
        检查是否有停止请求
        :param device_id: 设备ID
        :return: 是否有停止请求
        """
        return self._stop_flag.get(device_id, False)
    
    def disconnect_device(self, device_id: str):
        """
        断开设备连接
        :param device_id: 设备ID
        """
        if device_id in self._devices_pool:
            del self._devices_pool[device_id]
        if device_id in self._status:
            del self._status[device_id]
        if device_id in self._stop_flag:
            del self._stop_flag[device_id]
        self.logger.info(f"已断开设备连接: {device_id}")
    
    def get_connected_devices(self) -> List[str]:
        """
        获取已连接的设备ID列表
        :return: 设备ID列表
        """
        return list(self._devices_pool.keys())
    
    def is_device_connected(self, device_id: str) -> bool:
        """
        检查设备是否已连接
        :param device_id: 设备ID
        :return: 是否已连接
        """
        return device_id in self._devices_pool