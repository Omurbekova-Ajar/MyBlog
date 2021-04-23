from rest_framework import serializers
from rest_framework.utils import representation

from .models import Category, Post, PostImage, Rating, Like, Comment


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', read_only=True)
    class Meta:
        model = Post
        fields = ('id', 'title', 'category', 'created_at', 'text')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['category'] = CategorySerializer(instance.category).data
        representation['images'] = PostImageSerializer(instance.images.all(), many=True, context=self.context).data
        representation['rating'] = RatingSerializer(instance.ratings.all(), many=True, context=self.context).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        images = request.FILES
        validated_data['author_id'] = user_id
        post = Post.objects.create(**validated_data)
        for image in images.getlist('image'):
            PostImage.objects.create(post=post, image=image)
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.images.all().delete()
        images_data = request.FILES
        for image in images_data.getlist('image'):
            PostImage.objects.create(post=instance, image=image)
        return instance


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'

    def _get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
            else:
                url = ''
            return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('rating',)

    def validate(self, attrs):
        rating = attrs.get('rating')
        if rating:
            if rating > 5:
                raise serializers.ValidationError('The value must not exceed 5')
            return attrs
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        action = self.context.get('action')
        if action == 'create':
            fields.pop('user')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        print(validated_data)
        post = validated_data.get('post')
        rat = validated_data.get('rating')
        rating = Rating.objects.get_or_create(user=user, post=post)[0]
        rating.rating = rat
        rating.save()
        return rating

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.user.email
        return representation


class CommentSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%d %B %Y %H:%M', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'comment', 'post', 'created', 'user', 'parent')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create' or action == 'update':
            fields.pop('user')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['children'] = CommentSerializer(instance.children.all(), many=True, context=self.context).data
        return representation


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('user')
            fields.pop('like')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        like = Like.objects.get_or_create(user=user, post=post)[0]
        like.like = True if like.like is False else False
        like.save()
        return like
