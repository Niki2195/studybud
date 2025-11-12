from rest_framework import viewsets, permissions, filters
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer

# ViewSet для Room — оставляем как было
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by('-updated')
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


# ViewSet для Message — исправленный
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('created')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created']
    ordering = ['created']

    def get_queryset(self):
        queryset = super().get_queryset()
        room_id = self.request.query_params.get('room')
        if room_id:
            queryset = queryset.filter(room__id=room_id)
        return queryset.order_by('created')

    def perform_create(self, serializer):
        room_id = self.request.data.get('room')
        room = Room.objects.get(id=room_id)
        serializer.save(user=self.request.user, room=room)

    def partial_update(self, request, *args, **kwargs):
        message = self.get_object()
        message.read_by.add(request.user)
        message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data)