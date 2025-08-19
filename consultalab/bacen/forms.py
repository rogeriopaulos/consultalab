from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms
from validate_docbr import CNPJ
from validate_docbr import CPF

from consultalab.bacen.models import RequisicaoBacen


class RequisicaoBacenForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_requisicao"].label = ""
        self.fields["tipo_requisicao"].widget.attrs["type"] = "hidden"
        self.fields["termo_busca"].required = True
        self.fields["motivo"].required = True

    class Meta:
        model = RequisicaoBacen
        fields = [
            "tipo_requisicao",
            "termo_busca",
            "motivo",
        ]
        widgets = {
            "termo_busca": forms.TextInput(attrs={"class": "form-control"}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "termo_busca": "Termo de Busca (obrigatório)",
            "motivo": "Motivo (obrigatório)",
        }
        help_texts = {
            "termo_busca": (
                "Para tipos Pix CPF/CNPJ e CCS CPF/CNPJ, informe um CPF (11 dígitos) "
                "ou CNPJ (14 dígitos) válido."
            ),
            "motivo": "BO, IPL, Nº Caso LAB-LD, RIF, Processo Judicial...",
        }

    def clean(self):
        # Constantes para tamanhos de documentos
        cpf_length = 11
        cnpj_length = 14

        # Mensagens de erro
        msg_required = "O termo de busca é obrigatório para este tipo de requisição."
        msg_numeric_only = "O termo de busca deve conter apenas números."
        msg_invalid_cpf = "O termo de busca deve ser um CPF válido."
        msg_invalid_cnpj = "O termo de busca deve ser um CNPJ válido."
        msg_invalid_length = (
            "O termo de busca deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)."
        )

        cleaned_data = super().clean()
        termo_busca = cleaned_data.get("termo_busca")
        tipo_requisicao = cleaned_data.get("tipo_requisicao")

        if tipo_requisicao in ["1", "3"]:  # Pix CPF/CNPJ ou CCS CPF/CNPJ
            if not termo_busca:
                raise forms.ValidationError(msg_required)

            # Remove caracteres especiais, mantendo apenas dígitos
            termo_limpo = "".join(filter(str.isdigit, termo_busca))

            if not termo_limpo:
                raise forms.ValidationError(msg_numeric_only)

            # Verifica se é CPF (11 dígitos) ou CNPJ (14 dígitos)
            if len(termo_limpo) == cpf_length:
                cpf_validator = CPF()
                if not cpf_validator.validate(termo_limpo):
                    raise forms.ValidationError(msg_invalid_cpf)
            elif len(termo_limpo) == cnpj_length:
                cnpj_validator = CNPJ()
                if not cnpj_validator.validate(termo_limpo):
                    raise forms.ValidationError(msg_invalid_cnpj)
            else:
                raise forms.ValidationError(msg_invalid_length)

            # Atualiza o campo com o valor limpo (apenas números)
            cleaned_data["termo_busca"] = termo_limpo

        return cleaned_data


class RequisicaoBacenFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column(
                HTML(
                    """
                    <label for="id_created" class="form-label">
                        Data de criação
                    </label>
                    """,
                ),
                Field("created"),
            ),
            Column(
                Row(
                    Column(
                        Field(
                            HTML(
                                '<label for="div_id_created" class="form-label ms-5">Pesquisar</label>',  # noqa: E501
                            ),
                            "busca",
                            placeholder="cpf, cnpj, motivo...",
                        ),
                        css_class="col-8",
                    ),
                    Column(
                        HTML(
                            """
                            <button type="submit"
                                    class="btn btn-sm btn-outline-primary ms-5"
                                    id="filter-button">
                                <i class="bi bi-filter"></i> Filtrar
                            </button>
                            <a href="{% url 'core:home' %}"
                               class="text-decoration-none text-danger"
                               id="clear-filters"
                               data-bs-toggle="tooltip"
                               data-bs-placement="top"
                               data-bs-title="Limpar filtros">
                               <i class="bi bi-x-circle"></i>
                            </a>
                            """,
                        ),
                        css_class="col d-flex justify-content-around align-items-center",  # noqa: E501
                    ),
                    css_class="align-items-center",
                ),
                css_class="ms-5",
            ),
            css_class="d-flex justify-content-between align-items-center",
        ),
    )
