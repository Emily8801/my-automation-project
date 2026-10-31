"""模型调用封装：统一对接任意 OpenAI 兼容模型（智谱/通义/DeepSeek/GPT）

配置来源：config.yaml 的 llm 段；api_key 从环境变量 LLM_API_KEY 读取。
"""
import os
from pathlib import Path

import yaml
from openai import OpenAI

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config() -> dict:
    """读取 config.yaml，返回完整配置字典"""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_client(cfg: dict | None = None) -> OpenAI:
    """按配置创建模型客户端。base_url + model 决定连哪家，key 从环境变量取"""
    cfg = cfg or load_config()
    llm_cfg = cfg["llm"]
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("未设置环境变量 LLM_API_KEY（填在 .env 或系统环境变量里）")
    return OpenAI(base_url=llm_cfg["base_url"], api_key=api_key)


def chat(prompt: str, cfg: dict | None = None) -> str:
    """单轮对话：传入完整提示词，返回模型文本输出

    各 Stage（A/B/C/D）都通过这个函数调模型，提示词内容由 pipeline 负责拼装。
    """
    cfg = cfg or load_config()
    llm_cfg = cfg["llm"]
    client = get_client(cfg)
    resp = client.chat.completions.create(
        model=llm_cfg["model"],
        temperature=llm_cfg.get("temperature", 0.2),
        timeout=llm_cfg.get("timeout", 120),
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content
