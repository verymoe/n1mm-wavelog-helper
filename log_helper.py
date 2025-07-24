#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N1MM Wavelog 日志上传工具
功能：监听UDP端口，接收N1MM Logger发送的QSO数据，转换为ADIF格式后转发到Wavelog服务器
作者：BI3AR
版本：1.0
"""

import json
import socket
import requests
import logging
import sys
import re
from datetime import datetime
from typing import Dict, Any, Optional

def create_config_template(config_file: str = "config.json") -> None:
    """创建配置文件模板
    
    Args:
        config_file: 配置文件路径，默认为config.json
    """
    template = {
        "udp_port": 2333,  # UDP监听端口，N1MM Logger会向此端口发送数据
        "wavelog_url": "https://your-wavelog-url.com",  # Wavelog服务器地址
        "api_key": "your-api-key-here",  # Wavelog API密钥
        "station_profile_id": "1",  # 电台配置文件ID
        "listen_address": "0.0.0.0"  # 监听地址，0.0.0.0表示监听所有网卡
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"已创建配置文件模板: {config_file}")
        print("请编辑 config.json 文件，填入您的实际配置:")
        print("  - wavelog_url: 您的Wavelog服务器地址")
        print("  - api_key: 您的Wavelog API密钥")
        print("  - station_profile_id: 您的电台配置文件ID")
        print("  - udp_port: UDP监听端口 (默认: 2333)")
    except Exception as e:
        logging.error(f"Failed to create config template: {e}")

def load_config(config_file: str = "config.json") -> Optional[Dict[str, Any]]:
    """加载配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典，如果加载失败则返回None
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"配置文件 {config_file} 未找到")
        create_config_template(config_file)
        input("请编辑配置文件后按回车键退出...")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"配置文件JSON格式错误: {e}")
        logging.error("请检查 config.json 文件的语法错误")
        input("按回车键退出...")
        return None
    except Exception as e:
        logging.error(f"加载配置文件时出错: {e}")
        input("按回车键退出...")
        return None

def extract_xml_field(xml_data: str, field_name: str) -> Optional[str]:
    """从 XML 数据中提取指定字段的值
    
    Args:
        xml_data: XML 数据字符串
        field_name: 要提取的字段名称
        
    Returns:
        字段值，如果未找到则返回None
    """
    pattern = f'<{field_name}>(.*?)</{field_name}>'
    match = re.search(pattern, xml_data)
    return match.group(1) if match and match.group(1) else None

def convert_n1mm_to_adif(xml_data: str) -> Optional[str]:
    """将 N1MM Logger 的 XML 格式数据转换为 ADIF 格式
    
    Args:
        xml_data: N1MM Logger 发送的 XML 数据
        
    Returns:
        ADIF 格式字符串，如果转换失败则返回None
    """
    try:
        # 检查是否为 N1MM 的 contactinfo XML
        if '<contactinfo>' not in xml_data:
            return None
        
        adif_fields = []
        
        # 提取呼号
        call = extract_xml_field(xml_data, 'call')
        if call:
            adif_fields.append(f"<call:{len(call)}>{call}")
        
        # 提取频段（需要加上m后缀）
        #band = extract_xml_field(xml_data, 'band')
        #if band:
        #    band_text = band + "m"
        #    adif_fields.append(f"<band:{len(band_text)}>{band_text}")
        
        # 提取通信模式
        mode = extract_xml_field(xml_data, 'mode')
        if mode:
            adif_fields.append(f"<mode:{len(mode)}>{mode}")
        
        # 提取接收频率
        rxfreq = extract_xml_field(xml_data, 'rxfreq')
        if rxfreq:
            freq_mhz = str(float(rxfreq) / 100000)
            adif_fields.append(f"<freq_rx:{len(freq_mhz)}>{freq_mhz}")
        
        # 提取发射频率
        txfreq = extract_xml_field(xml_data, 'txfreq')
        if txfreq:
            freq_mhz = str(float(txfreq) / 100000)
            adif_fields.append(f"<freq:{len(freq_mhz)}>{freq_mhz}")
        
        # 提取时间戳并转换为ADIF格式
        timestamp = extract_xml_field(xml_data, 'timestamp')
        if timestamp:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            qso_date = dt.strftime('%Y%m%d')  # QSO日期 YYYYMMDD
            time_on = dt.strftime('%H%M%S')   # QSO时间 HHMMSS
            adif_fields.append(f"<qso_date:{len(qso_date)}>{qso_date}")
            adif_fields.append(f"<time_on:{len(time_on)}>{time_on}")
            adif_fields.append(f"<time_off:{len(time_on)}>{time_on}")
        
        # 提取接收和发送的RST信号报告
        rcv = extract_xml_field(xml_data, 'rcv')
        if rcv:
            adif_fields.append(f"<rst_rcvd:{len(rcv)}>{rcv}")
        
        snt = extract_xml_field(xml_data, 'snt')
        if snt:
            adif_fields.append(f"<rst_sent:{len(snt)}>{snt}")
        
        # 提取其他可选信息
        name = extract_xml_field(xml_data, 'name')  # 姓名
        if name:
            adif_fields.append(f"<name:{len(name)}>{name}")
        
        gridsquare = extract_xml_field(xml_data, 'gridsquare')  # 网格坐标
        if gridsquare:
            adif_fields.append(f"<gridsquare:{len(gridsquare)}>{gridsquare}")
        
        qth = extract_xml_field(xml_data, 'qth')  # 位置
        if qth:
            adif_fields.append(f"<qth:{len(qth)}>{qth}")
        
        comment = extract_xml_field(xml_data, 'comment')  # 备注
        if comment:
            adif_fields.append(f"<comment:{len(comment)}>{comment}")
        
        # 添加记录结束标记
        adif_fields.append("<eor>")
        
        return ''.join(adif_fields)
        
    except Exception as e:
        logging.error(f"Error converting N1MM to ADIF: {e}")
        return None

def send_to_wavelog(data: str, config: Dict[str, Any], max_retries: int = 3) -> bool:
    """向 Wavelog 服务器发送 ADIF 数据
    
    Args:
        data: ADIF 格式的 QSO 数据
        config: 配置字典
        max_retries: 最大重试次数
        
    Returns:
        发送成功返回True，失败返回False
    """
    url = f"{config['wavelog_url']}/api/qso"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "key": config["api_key"],
        "station_profile_id": config["station_profile_id"],
        "type": "adif",
        "string": data
    }
    
    # 重试机制：最多重试3次，指数退避
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            logging.info(f"成功发送数据到 Wavelog: {response.status_code}")
            return True
        except requests.exceptions.Timeout:
            logging.warning(f"第 {attempt + 1}/{max_retries} 次尝试超时")
            if attempt == max_retries - 1:
                logging.error("所有重试都超时，发送数据失败")
        except requests.exceptions.ConnectionError:
            logging.warning(f"第 {attempt + 1}/{max_retries} 次尝试连接错误")
            if attempt == max_retries - 1:
                logging.error("所有重试都无法连接到服务器")
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logging.warning(f"第 {attempt + 1}/{max_retries} 次请求错误: {e}")
            if attempt == max_retries - 1:
                logging.error(f"所有重试后仍无法发送数据: {e}")
        
        # 指数退避：第1次等待2秒，第2次等待4秒
        if attempt < max_retries - 1:
            import time
            time.sleep(2 ** attempt)
    
    return False

def start_udp_listener(config: Dict[str, Any]):
    """启动 UDP 监听器，接收 N1MM Logger 发送的数据
    
    Args:
        config: 配置字典
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((config["listen_address"], config["udp_port"]))
        logging.info(f"UDP 监听器已启动，监听地址: {config['listen_address']}:{config['udp_port']}")
        logging.info("等待 N1MM 数据... (按 Ctrl+C 停止)")
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                received_data = data.decode('utf-8').strip()
                logging.info(f"从 {addr} 接收到数据")
                
                if received_data:
                    # 检查是否为 XML 格式数据
                    if received_data.startswith('<?xml'):
                        # 转换 N1MM XML 数据为 ADIF 格式
                        adif_data = convert_n1mm_to_adif(received_data)
                        if adif_data:
                            logging.info(f"XML 已转换为 ADIF: {adif_data}")
                            success = send_to_wavelog(adif_data, config)
                            if not success:
                                logging.warning("发送到 Wavelog 失败，但继续监听...")
                        else:
                            logging.warning("转换 N1MM XML 为 ADIF 失败")
                    else:
                        # 非 XML 数据，直接发送
                        logging.info(f"接收到非 XML 数据: {received_data[:100]}...")
                        success = send_to_wavelog(received_data, config)
                        if not success:
                            logging.warning("发送到 Wavelog 失败，但继续监听...")
                    
            except UnicodeDecodeError:
                logging.warning(f"从 {addr} 接收到非 UTF-8 数据，跳过...")
            except Exception as e:
                logging.error(f"处理接收数据时出错: {e}")
                logging.info("继续监听新数据...")
                
    except OSError as e:
        if e.errno == 10048:
            logging.error(f"端口 {config['udp_port']} 已被占用！")
            logging.error("请检查是否有其他实例正在运行，或在 config.json 中修改端口")
        else:
            logging.error(f"Socket 错误: {e}")
    except Exception as e:
        logging.error(f"UDP 监听器错误: {e}")
    finally:
        sock.close()
        logging.info("UDP 监听器已停止")

def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置文件的完整性和有效性
    
    Args:
        config: 配置字典
        
    Returns:
        配置有效返回True，无效返回False
    """
    required_keys = ["udp_port", "wavelog_url", "api_key", "station_profile_id"]
    missing_keys = []
    
    # 检查是否缺少必要的配置项或使用了默认模板值
    for key in required_keys:
        if key not in config or not config[key] or config[key] == f"your-{key.replace('_', '-')}-here":
            missing_keys.append(key)
    
    if missing_keys:
        logging.error("配置验证失败！")
        logging.error(f"缺少或无效的配置项: {', '.join(missing_keys)}")
        logging.error("请编辑 config.json 填入您的实际 Wavelog 设置")
        return False
    
    return True

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('log_helper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("N1MM Wavelog 日志上传工具 v1.0")
    print("================================")
    
    config = load_config()
    if config is None:
        return
    
    if not validate_config(config):
        input("按回车键退出...")
        return
    
    if "listen_address" not in config:
        config["listen_address"] = "0.0.0.0"
    
    try:
        logging.info(f"在 {config['listen_address']}:{config['udp_port']} 上启动监听服务")
        logging.info(f"转发目标: {config['wavelog_url']}")
        start_udp_listener(config)
    except KeyboardInterrupt:
        logging.info("用户停止了服务")
    except Exception as e:
        logging.error(f"意外错误: {e}")
        input("按回车键退出...")
    finally:
        logging.info("日志服务已停止")

if __name__ == "__main__":
    main()