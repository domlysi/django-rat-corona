from rest_framework import generics, status
from rest_framework.response import Response

from apps.corona.models import Command, CommandResult
from apps.corona.serializers import ClientSerializer, CommandSerializer, CommandResultSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class RegisterClientView(generics.CreateAPIView):
    serializer_class = ClientSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.initial_data['last_ip'] = get_client_ip(self.request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommandsView(generics.ListAPIView):
    serializer_class = CommandSerializer

    def get_queryset(self):
        return Command.objects.filter(client__uuid=self.request.GET.get('id'), received=False)

    def get(self, request, *args, **kwargs):
        r = super().get(request, *args, **kwargs)
        self.get_queryset().update(received=True)
        return r


class CommandResultListView(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = CommandResultSerializer
    queryset = CommandResult.objects.all()


class CommandResultView(generics.RetrieveAPIView):
    def get_object(self):
        command_uuid = self.kwargs.get('uuid')
        return CommandResult.objects.get(command__uuid=command_uuid)