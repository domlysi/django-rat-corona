from rest_framework import serializers

from apps.corona.models import Client, Command, CommandResult


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ['created_on', 'updated_on', ]

    def create(self, validated_data):
        try:
            return Client.objects.get(**validated_data)
        except Client.MultipleObjectsReturned:
            Client.objects.filter(**validated_data).delete()
            return super().create(validated_data)
        except Client.DoesNotExist:
            return super().create(validated_data)


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        exclude = ['id', 'client', 'received']


class CommandResultSerializer(serializers.ModelSerializer):
    command = serializers.CharField(source='command.uuid')

    class Meta:
        model = CommandResult
        exclude = ['id', ]

    def create(self, validated_data):
        try:
            command = Command.objects.get(**validated_data.pop('command'))
        except Exception as e:
            raise e
        validated_data['command'] = command
        return super().create(validated_data)



