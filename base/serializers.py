from rest_framework import serializers
from .models import Room, Message


class RoomSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField(read_only=True)
    topic = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'description','updated', 'created', 'topic', 'host']


class MessageSerializer(serializers.ModelSerializer):
    # user только для чтения
    user = serializers.StringRelatedField(read_only=True)
    # room будет записываться при создании
    room = serializers.PrimaryKeyRelatedField(read_only=True)
    read_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'room', 'body', 'updated', 'created','read_by']
