from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, data):
        # Валидация продолжительности
        if data.get('duration', 0) > 120:
            raise serializers.ValidationError(
                "Время выполнения не может превышать 120 секунд."
            )

        # Валидация периодичности
        if data.get('frequency', 1) > 7:
            raise serializers.ValidationError(
                "Периодичность не может быть реже раза в неделю."
            )

        # Получаем текущие данные (если они есть) для частичного обновления
        instance = self.instance
        is_pleasant = data.get('is_pleasant', instance.is_pleasant if instance else False)
        reward = data.get('reward', instance.reward if instance else None)
        linked_habit = data.get('linked_habit', instance.linked_habit if instance else None)

        # Валидация приятной привычки
        if is_pleasant and (reward or linked_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        # Валидация взаимного исключения reward и linked_habit
        if reward and linked_habit:
            raise serializers.ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку."
            )

        # Валидация linked_habit (должна быть приятной)
        if linked_habit and not linked_habit.is_pleasant:
            raise serializers.ValidationError(
                "В связанные привычки можно добавлять только приятные привычки."
            )

        return data

    def create(self, validated_data):
        # Автоматически устанавливаем пользователя из запроса
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
