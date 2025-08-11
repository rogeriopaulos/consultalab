from django import forms


class ReportTypeForm(forms.Form):
    """Formulário para seleção do tipo de relatório"""

    REPORT_TYPE_CHOICES = [
        ("summary", "Resumido"),
        ("detailed", "Detalhado"),
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        initial="detailed",
        widget=forms.RadioSelect(
            attrs={
                "class": "form-check-input",
            },
        ),
        label="Tipo de Relatório",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["report_type"].widget.attrs.update(
            {
                "class": "form-check-input me-2",
            },
        )
