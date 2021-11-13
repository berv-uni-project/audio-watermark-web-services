from rest_framework import serializers

from .models import Embed, Extract

class EmbedSerializer(serializers.HyperlinkedModelSerializer):  
    class Meta:
        model = Embed
        fields = '__all__'

class ExtractSerializer(serializers.HyperlinkedModelSerializer):  
    class Meta:
        model = Extract
        fields = '__all__'