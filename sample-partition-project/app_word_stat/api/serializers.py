from rest_framework import serializers


class TaskId(serializers.Serializer):
    task_id = serializers.IntegerField()


class CreateTask(serializers.Serializer):
    """
    Returns a list of all **active** accounts in the system.

    For more details on how accounts are activated please [see here][ref].

    [ref]: http://example.com/activating-accounts
    """
    text = serializers.CharField()
    period = serializers.IntegerField()
    device = serializers.IntegerField()
    region = serializers.IntegerField()
