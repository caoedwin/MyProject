"""AI 视图 - 对话 / 流式对话 / 会话历史"""
import json
from django.http import StreamingHttpResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from aihub.models import ChatSession, ChatMessage
from aihub import client as ai_client
from system.utils import ok, fail


class ChatMessageSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'role_name', 'content', 'tokens', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'model', 'messages', 'created_at', 'updated_at']


class ChatViewSet(viewsets.ModelViewSet):
    """AI 对话接口"""
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(ok(serializer.data))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(ok(serializer.data))

    @action(detail=False, methods=['post'], url_path='ask')
    def ask(self, request):
        """单轮对话（非流式）"""
        content = request.data.get('content', '').strip()
        session_id = request.data.get('session_id')
        system_prompt = request.data.get('system_prompt', '你是一个有帮助的助手。')
        if not content:
            return Response(fail(msg='内容不能为空'))

        # 获取或创建会话
        if session_id:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=content[:30],
                model=request.data.get('model', ''),
            )

        # 保存用户消息
        ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=content)

        # 构建消息上下文（最近 10 条 + system）
        history = ChatMessage.objects.filter(session=session).order_by('-created_at')[:10]
        history = reversed(list(history))
        messages = [{'role': 'system', 'content': system_prompt}]
        for m in history:
            role = {0: 'system', 1: 'user', 2: 'assistant'}.get(m.role, 'user')
            messages.append({'role': role, 'content': m.content})

        try:
            result = ai_client.chat(messages)
        except Exception as e:
            return Response(fail(msg=f'AI 调用失败: {e}', code=503))

        # 保存 AI 回复
        ChatMessage.objects.create(
            session=session, role=ChatMessage.Role.ASSISTANT,
            content=result['content'],
            tokens=result.get('usage', {}).get('total_tokens', 0) if result.get('usage') else 0,
        )
        return Response(ok({
            'session_id': session.id,
            'content': result['content'],
            'usage': result.get('usage'),
        }))

    @action(detail=False, methods=['post'], url_path='ask-stream')
    def ask_stream(self, request):
        """流式对话（SSE）"""
        content = request.data.get('content', '').strip()
        session_id = request.data.get('session_id')
        system_prompt = request.data.get('system_prompt', '你是一个有帮助的助手。')
        if not content:
            return Response(fail(msg='内容不能为空'))

        if session_id:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user, title=content[:30],
                model=request.data.get('model', ''),
            )
        ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=content)

        history = list(reversed(list(
            ChatMessage.objects.filter(session=session).order_by('-created_at')[:10]
        )))
        messages = [{'role': 'system', 'content': system_prompt}]
        for m in history:
            role = {0: 'system', 1: 'user', 2: 'assistant'}.get(m.role, 'user')
            messages.append({'role': role, 'content': m.content})

        def stream():
            full_content = []
            try:
                for chunk in ai_client.chat_stream(messages):
                    full_content.append(chunk)
                    yield f'data: {json.dumps({"content": chunk}, ensure_ascii=False)}\n\n'
                # 流结束后保存完整回复
                ChatMessage.objects.create(
                    session=session, role=ChatMessage.Role.ASSISTANT,
                    content=''.join(full_content),
                )
                yield f'data: {json.dumps({"done": True, "session_id": session.id}, ensure_ascii=False)}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'

        resp = StreamingHttpResponse(stream(), content_type='text/event-stream')
        resp['Cache-Control'] = 'no-cache'
        resp['X-Accel-Buffering'] = 'no'
        return resp
