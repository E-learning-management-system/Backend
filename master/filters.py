from django_filters import rest_framework as filters
from master.models import Exercise


class TicketFilter(filters.FilterSet):

    class Meta:
        model = Exercise
        fields = ['status']
