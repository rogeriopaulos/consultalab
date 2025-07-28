import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.forms import TextInput

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    date_joined = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={
                "placeholder": "YYYY/MM/DD",
                "type": "date",
                "class": "form-control form-control-sm",
            },
        ),
        label="Registrado entre",
    )
    busca = django_filters.CharFilter(
        label="Busca",
        method="filter_busca",
        widget=TextInput(
            attrs={
                "class": "form-control form-control-sm",
            },
        ),
    )

    class Meta:
        model = User
        fields = ["busca", "is_active", "date_joined"]
        order_by = ["-date_joined"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields["is_active"].widget.attrs.update(
            {"class": "form-select form-select-sm"},
        )

    def filter_busca(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(email__icontains=value),
        )
