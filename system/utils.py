"""统一响应工具 - 前后端分离标准 JSON 结构"""


def ok(data=None, msg='success', code=200):
    """成功响应"""
    payload = {'code': code, 'msg': msg, 'success': True}
    if data is not None:
        payload['data'] = data
    return payload


def fail(msg='error', code=400, data=None, err=None):
    """失败响应"""
    payload = {'code': code, 'msg': msg, 'success': False}
    if data is not None:
        payload['data'] = data
    if err is not None:
        payload['err'] = err
    return payload


def page_result(items, total, page, page_size):
    """分页结果"""
    return {
        'code': 200,
        'msg': 'success',
        'success': True,
        'data': {
            'list': items,
            'total': total,
            'page': page,
            'page_size': page_size,
        },
    }
