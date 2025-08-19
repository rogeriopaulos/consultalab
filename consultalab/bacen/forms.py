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

# Constantes
MIN_CAMPOS_LINHA = 3
CPF_LENGTH = 11
CNPJ_LENGTH = 14
CAMPO_REFERENCIA_INDEX = 3


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


class BulkRequestForm(forms.Form):
    arquivo_txt = forms.FileField(
        label="Arquivo TXT",
        help_text="Selecione um arquivo TXT com as requisições em lote",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": ".txt",
            },
        ),
    )

    def clean_arquivo_txt(self):
        arquivo = self.cleaned_data.get("arquivo_txt")

        if not arquivo:
            msg = "É necessário selecionar um arquivo."
            raise forms.ValidationError(msg)

        # Verifica se é um arquivo TXT
        if not arquivo.name.endswith(".txt"):
            msg = "O arquivo deve ter extensão .txt"
            raise forms.ValidationError(msg)

        # Verifica o tamanho do arquivo (máximo 5MB)
        if arquivo.size > 5 * 1024 * 1024:
            msg = "O arquivo não pode ser maior que 5MB."
            raise forms.ValidationError(msg)

        return arquivo

    def _validate_line_fields(self, campos, num_linha, linha):
        """Valida se a linha tem campos suficientes."""
        if len(campos) < MIN_CAMPOS_LINHA:
            msg = (
                "Linha deve conter pelo menos 3 campos: "
                "tipo_requisicao, termo_busca, motivo"
            )
            return {
                "linha": num_linha,
                "conteudo": linha,
                "erro": msg,
            }
        return None

    def _validate_tipo_requisicao(self, tipo_requisicao, num_linha, linha):
        """Valida o tipo de requisição."""
        if tipo_requisicao not in ["1", "2"]:
            msg = "tipo_requisicao deve ser 1 (Pix CPF/CNPJ) ou 2 (Pix Chave)"
            return {
                "linha": num_linha,
                "conteudo": linha,
                "erro": msg,
            }
        return None

    def _validate_required_fields(self, termo_busca, motivo, num_linha, linha):
        """Valida se campos obrigatórios estão preenchidos."""
        if not termo_busca or not motivo:
            return {
                "linha": num_linha,
                "conteudo": linha,
                "erro": "termo_busca e motivo são obrigatórios",
            }
        return None

    def _validate_cpf_cnpj(self, termo_busca, num_linha, linha):
        """Valida CPF/CNPJ e retorna o termo limpo ou erro."""
        # Remove caracteres especiais, mantendo apenas dígitos
        termo_limpo = "".join(filter(str.isdigit, termo_busca))

        if not termo_limpo:
            msg = "Para Pix CPF/CNPJ, o termo de busca deve conter apenas números"
            return None, {
                "linha": num_linha,
                "conteudo": linha,
                "erro": msg,
            }

        # Verifica se é CPF (11 dígitos) ou CNPJ (14 dígitos)
        if len(termo_limpo) == CPF_LENGTH:
            cpf_validator = CPF()
            if not cpf_validator.validate(termo_limpo):
                return None, {
                    "linha": num_linha,
                    "conteudo": linha,
                    "erro": "CPF inválido",
                }
        elif len(termo_limpo) == CNPJ_LENGTH:
            cnpj_validator = CNPJ()
            if not cnpj_validator.validate(termo_limpo):
                return None, {
                    "linha": num_linha,
                    "conteudo": linha,
                    "erro": "CNPJ inválido",
                }
        else:
            msg = (
                "Para Pix CPF/CNPJ, o termo deve ter 11 dígitos (CPF) "
                "ou 14 dígitos (CNPJ)"
            )
            return None, {
                "linha": num_linha,
                "conteudo": linha,
                "erro": msg,
            }

        return termo_limpo, None

    def _validate_user_permissions(self, tipo_requisicao, user, num_linha, linha):
        """Valida se o usuário tem permissão para o tipo de requisição."""
        if tipo_requisicao in ["1", "2"] and not user.has_perm("users.can_request_pix"):
            return {
                "linha": num_linha,
                "conteudo": linha,
                "erro": "Usuário não autorizado a realizar requisições Pix",
            }
        return None

    def _process_single_line(self, linha_original, num_linha, user):
        """Processa uma única linha do arquivo."""
        linha = linha_original.strip()
        if not linha:  # Pula linhas vazias
            return None, None

        # Divide a linha por vírgula ou ponto e vírgula
        if ";" in linha:
            campos = [campo.strip() for campo in linha.split(";")]
        else:
            campos = [campo.strip() for campo in linha.split(",")]

        # Executa todas as validações em sequência
        erro = (
            self._validate_line_fields(campos, num_linha, linha)
            or self._validate_tipo_requisicao(campos[0].strip(), num_linha, linha)
            or self._validate_required_fields(
                campos[1].strip(),
                campos[2].strip(),
                num_linha,
                linha,
            )
        )

        if erro:
            return None, erro

        tipo_requisicao = campos[0].strip()
        termo_busca = campos[1].strip()
        motivo = campos[2].strip()
        referencia = (
            campos[CAMPO_REFERENCIA_INDEX].strip()
            if len(campos) > CAMPO_REFERENCIA_INDEX
            else ""
        )

        # Valida CPF/CNPJ para tipo_requisicao = 1
        if tipo_requisicao == "1":
            termo_limpo, erro = self._validate_cpf_cnpj(
                termo_busca,
                num_linha,
                linha,
            )
            if erro:
                return None, erro
            termo_busca = termo_limpo

        # Valida permissões do usuário
        erro = self._validate_user_permissions(tipo_requisicao, user, num_linha, linha)
        if erro:
            return None, erro

        # Se chegou até aqui, a requisição é válida
        requisicao_valida = {
            "tipo_requisicao": tipo_requisicao,
            "termo_busca": termo_busca,
            "motivo": motivo,
            "referencia": referencia,
            "user": user,
        }

        return requisicao_valida, None

    def process_file(self, user):
        """
        Processa o arquivo TXT e retorna uma lista de requisições válidas e inválidas.
        """
        arquivo = self.cleaned_data["arquivo_txt"]

        # Lê o conteúdo do arquivo
        try:
            conteudo = arquivo.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                conteudo = arquivo.read().decode("latin-1")
            except UnicodeDecodeError as err:
                msg = (
                    "Não foi possível decodificar o arquivo. "
                    "Certifique-se de que está em formato UTF-8 ou Latin-1."
                )
                raise forms.ValidationError(msg) from err

        linhas = conteudo.strip().split("\n")
        requisicoes_validas = []
        requisicoes_invalidas = []

        # Processa cada linha
        for num_linha, linha_original in enumerate(linhas, 1):
            requisicao_valida, erro = self._process_single_line(
                linha_original,
                num_linha,
                user,
            )

            if erro:
                requisicoes_invalidas.append(erro)
            elif requisicao_valida:
                requisicoes_validas.append(requisicao_valida)

        return requisicoes_validas, requisicoes_invalidas
