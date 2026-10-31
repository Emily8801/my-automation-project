"""模型调用封装：读 config.yaml 的 llm 段，api_key 用 ${ENV} 形式从环境变量展开"""
import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 加载 .env，让 ${LLM_API_KEY} 能从里面取值


def _cfg(p="config.yaml"):
    return yaml.safe_load(open(p, encoding="utf-8"))


def chat(prompt, cfg_path="config.yaml"):
    """单轮对话：传入完整提示词，返回模型文本输出（各 Stage 统一走这里）"""
    c = _cfg(cfg_path)["llm"]
    api_key = os.path.expandvars(c["api_key"])      # "${LLM_API_KEY}" → 环境变量的值
    client = OpenAI(base_url=c["base_url"], api_key=api_key)
    r = client.chat.completions.create(
        model=c["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=c.get("temperature", 0.2),
        timeout=c.get("timeout", 120),
    )
    return r.choices[0].message.content
