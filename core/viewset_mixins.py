class SerializerMapMixin:
    """
    Add ...
    """

    def get_serializer_class(self):
        return self.serializer_class_map.get(self.action, self.serializer_class)  # noqa: E501
