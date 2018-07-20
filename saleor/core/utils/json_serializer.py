from django.core.serializers.json import (
    DjangoJSONEncoder, Serializer as JsonSerializer,
    Deserializer as JsonDeserializer)
import json

from django.core.serializers.base import DeserializationError
from django.core.serializers.python import (
    Deserializer as PythonDeserializer, Serializer as PythonSerializer,
)

from prices import Money

class Serializer(JsonSerializer):
    def _init_options(self):
        super()._init_options()
        self.json_kwargs['cls'] = CustomJsonEncoder


def Deserializer(stream_or_string, **options):
    """Deserialize a stream or string of JSON data."""
    if not isinstance(stream_or_string, (bytes, str)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode()
    try:
        objects = json.loads(stream_or_string)
        yield from PythonDeserializer(objects, **options)
    except Exception as exc:
        raise DeserializationError() from exc    


class CustomJsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Money):
            return "{}".format(obj.amount)
        return super().default(obj)