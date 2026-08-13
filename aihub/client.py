"""AI 客户端封装 - 支持 OpenAI 兼容协议，可切换 provider"""
import logging
from django.conf import settings
from openai import OpenAI, APITimeoutError, APIConnectionError, AuthenticationError

logger = logging.getLogger('aihub')

# 超时友好错误提示映射
_TIMEOUT_MSG = (
    'AI 服务连接超时，请检查：\n'
    '1. 网络是否能访问 {base_url}\n'
    '2. 是否需要配置代理（HTTP_PROXY / HTTPS_PROXY 环境变量）\n'
    '3. 当前超时设置为 {timeout} 秒，可在 .env 中设置 AI_TIMEOUT 调大'
)

_AUTH_MSG = (
    'AI API Key 无效或未配置，请在 .env 中设置 AI_API_KEY'
)

_CONNECTION_MSG = (
    '无法连接到 AI 服务 ({base_url})，请检查网络或 AI_BASE_URL 配置'
)


def get_client():
    """获取 AI 客户端（OpenAI 兼容）"""
    return OpenAI(
        api_key=settings.AI_API_KEY or 'sk-placeholder',
        base_url=settings.AI_BASE_URL,
        timeout=settings.AI_TIMEOUT,
        max_retries=settings.AI_MAX_RETRIES,
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
    except APITimeoutError:
        msg = _TIMEOUT_MSG.format(
            base_url=settings.AI_BASE_URL,
            timeout=settings.AI_TIMEOUT,
        )
        logger.error(msg)
        raise RuntimeError(msg) from None
    except APIConnectionError:
        msg = _CONNECTION_MSG.format(base_url=settings.AI_BASE_URL)
        logger.error(msg)
        raise RuntimeError(msg) from None
    except AuthenticationError:
        logger.error(_AUTH_MSG)
        raise RuntimeError(_AUTH_MSG) from None
    except Exception as e:
        logger.exception('AI 调用失败: %s', e)
        raise


def chat_stream(messages, model=None, temperature=0.7):
    """流式对话 - 生成器，逐块返回 content"""
    resp = chat(messages, model=model, temperature=temperature, stream=True)
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content