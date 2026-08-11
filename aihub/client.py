"""AI 客户端封装 - 支持 OpenAI 兼容协议，可切换 provider"""
import logging
from django.conf import settings

logger = logging.getLogger('aihub')


def get_client():
    """获取 AI 客户端（OpenAI 兼容）"""
    from openai import OpenAI
    return OpenAI(
        api_key=settings.AI_API_KEY or 'sk-placeholder',
        base_url=settings.AI_BASE_URL,
    )


def chat(messages, model=None, temperature=0.7, stream=False):
    """对话接口 - messages: [{role, content}, ...]"""
    client = get_client()
    model = model or settings.AI_MODEL
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=stream,
        )
        if stream:
            return resp  # 返回迭代器
        return {
            'content': resp.choices[0].message.content,
            'model': resp.model,
            'usage': {
                'prompt_tokens': resp.usage.prompt_tokens,
                'completion_tokens': resp.usage.completion_tokens,
                'total_tokens': resp.usage.total_tokens,
            } if resp.usage else None,
        }
    except Exception as e:
        logger.exception('AI 调用失败: %s', e)
        raise


def chat_stream(messages, model=None, temperature=0.7):
    """流式对话 - 生成器，逐块返回 content"""
    resp = chat(messages, model=model, temperature=temperature, stream=True)
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
