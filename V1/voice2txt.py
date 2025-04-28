import argparse
import os
import json
from openai import OpenAI, APIError

class ConfigManager:
    """管理配置的加载和保存。"""
    
    def __init__(self, config_file="whisper_config.json"):
        """
        初始化ConfigManager，指定配置文件路径。
        
        Args:
            config_file (str): 配置文件路径。默认为"whisper_config.json"。
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """
        从JSON文件加载配置（如果存在）。
        
        Returns:
            dict: 加载的配置，如果文件不存在则返回空字典。
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取配置文件时出错: {e}")
                return {}
        return {}
    
    def save_config(self, config_values):
        """
        将配置值保存到JSON文件。
        
        Args:
            config_values (dict): 要保存的配置值。
        """
        # 用新值更新当前配置
        self.config.update(config_values)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
    
    def get(self, key, default=None):
        """
        获取配置值。
        
        Args:
            key (str): 配置键。
            default: 如果键不存在，返回的默认值。
            
        Returns:
            配置值或默认值。
        """
        return self.config.get(key, default)

def transcribe_audio(file_path, client):
    """
    使用Whisper API端点转录音频文件。

    Args:
        file_path (str): 音频文件路径。
        client (OpenAI): 已配置的OpenAI客户端。

    Returns:
        str: 转录的文本，如果出错则返回None。
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            print(f"错误：找不到文件 {file_path}")
            return None

        # 以二进制读取模式打开音频文件
        with open(file_path, "rb") as audio_file:
            # 调用API进行转录
            print(f"正在上传并转录文件: {file_path}...")
            if client.base_url:
                print(f"使用 API 端点: {client.base_url}")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # 模型名称可能需要根据第三方服务调整
                file=audio_file
            )
        print("转录完成.")
        return transcript.text

    except APIError as e:
        # 尝试提供更详细的错误信息（如果可用）
        error_details = e.response.text if hasattr(e, 'response') and hasattr(e.response, 'text') else str(e)
        print(f"API 返回错误: {error_details}")
        return None
    except Exception as e:
        print(f"发生意外错误: {e}")
        return None

if __name__ == "__main__":
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 设置参数解析器
    parser = argparse.ArgumentParser(description="使用 Whisper API 转录音频文件。")
    parser.add_argument("audio_file", help="要转录的音频文件的路径。")
    parser.add_argument("--base-url", help="第三方 Whisper API 的 Base URL。", default=None)
    parser.add_argument("--api-key", help="API 密钥 (如果未设置 OPENAI_API_KEY 环境变量)。", default=None)
    parser.add_argument("--save", action="store_true", help="保存当前的 base-url 和 api-key 到配置文件中。")
    
    # 解析参数
    args = parser.parse_args()
    
    # 确定要使用的API密钥:
    # 1. 命令行参数（最高优先级）
    # 2. 保存的配置（中等优先级）
    # 3. 环境变量（最低优先级）
    api_key_to_use = args.api_key or config_manager.get("api_key") or os.getenv("OPENAI_API_KEY")
    
    if not api_key_to_use:
        print("错误：请设置 OPENAI_API_KEY 环境变量，使用 --api-key 参数提供 API 密钥，或先使用 --save 保存配置。")
        exit(1)
    
    # 确定要使用的base URL:
    # 1. 命令行参数（最高优先级）
    # 2. 保存的配置（最低优先级）
    base_url_to_use = args.base_url or config_manager.get("base_url")
    
    # 使用确定的参数初始化OpenAI客户端
    openai_client_args = {"api_key": api_key_to_use}
    if base_url_to_use:
        openai_client_args["base_url"] = base_url_to_use
    
    client = OpenAI(**openai_client_args)
    
    # 如果需要，保存配置
    if args.save:
        config_to_save = {}
        if args.api_key:
            config_to_save["api_key"] = args.api_key
        if args.base_url:
            config_to_save["base_url"] = args.base_url
        
        # 只有当至少提供了一个配置值时才保存
        if config_to_save:
            config_manager.save_config(config_to_save)
        else:
            print("警告：没有提供要保存的配置值。请使用 --api-key 或 --base-url 指定要保存的值。")
    
    # 获取转录
    transcription = transcribe_audio(args.audio_file, client)
    
    # 如果成功，打印转录结果
    if transcription:
        print("\n转录结果:")
        print(transcription)