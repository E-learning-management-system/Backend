from django_filters import rest_framework as filters
from master.models import Exercise


class ExerciseFilter(filters.FilterSet):

    class Meta:
        model = Exercise
        fields = []
