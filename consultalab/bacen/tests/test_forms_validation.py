"""
Testes para validação de CPF e CNPJ no formulário RequisicaoBacenForm.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from consultalab.bacen.forms import RequisicaoBacenForm

User = get_user_model()


class TestRequisicaoBacenFormValidation(TestCase):
    """Testes para validação de CPF e CNPJ no formulário."""

    def setUp(self):
        """Configuração inicial dos testes."""
        test_password = "testpass123"  # noqa: S105
        self.user = User.objects.create_user(
            email="test@example.com",
            password=test_password,
        )

    def test_cpf_valido(self):
        """Testa se um CPF válido é aceito."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "11144477735",  # CPF válido
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert form.is_valid(), f"Erros: {form.errors}"

    def test_cpf_invalido(self):
        """Testa se um CPF inválido é rejeitado."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "11111111111",  # CPF inválido (todos os dígitos iguais)
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert not form.is_valid()
        assert "O termo de busca deve ser um CPF válido." in str(form.errors)

    def test_cnpj_valido(self):
        """Testa se um CNPJ válido é aceito."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "11222333000181",  # CNPJ válido
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert form.is_valid(), f"Erros: {form.errors}"

    def test_cnpj_invalido(self):
        """Testa se um CNPJ inválido é rejeitado."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "11111111111111",  # CNPJ inválido (todos os dígitos iguais)
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert not form.is_valid()
        assert "O termo de busca deve ser um CNPJ válido." in str(form.errors)

    def test_cpf_com_formatacao(self):
        """Testa se um CPF com formatação é aceito e limpo."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "111.444.777-35",  # CPF válido com formatação
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert form.is_valid(), f"Erros: {form.errors}"
        # Verifica se o campo foi limpo (sem formatação)
        assert form.cleaned_data["termo_busca"] == "11144477735"

    def test_cnpj_com_formatacao(self):
        """Testa se um CNPJ com formatação é aceito e limpo."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "11.222.333/0001-81",  # CNPJ válido com formatação
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert form.is_valid(), f"Erros: {form.errors}"
        # Verifica se o campo foi limpo (sem formatação)
        assert form.cleaned_data["termo_busca"] == "11222333000181"

    def test_documento_com_tamanho_incorreto(self):
        """Testa se documentos com tamanho incorreto são rejeitados."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "12345",  # Tamanho incorreto
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert not form.is_valid()
        assert "O termo de busca deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)" in str(
            form.errors,
        )

    def test_termo_busca_vazio_tipo_1(self):
        """Testa se termo de busca vazio é rejeitado para tipo 1."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "",
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert not form.is_valid()
        assert "O termo de busca é obrigatório para este tipo de requisição" in str(
            form.errors,
        )

    def test_termo_busca_nao_numerico(self):
        """Testa se termo de busca não numérico é rejeitado."""
        form_data = {
            "tipo_requisicao": "1",  # Pix CPF/CNPJ
            "termo_busca": "abcdefghijk",
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert not form.is_valid()
        assert "O termo de busca deve conter apenas números" in str(form.errors)

    def test_validacao_nao_aplicada_tipo_2(self):
        """Testa se a validação não é aplicada para tipo de requisição 2 (Pix Chave)."""
        form_data = {
            "tipo_requisicao": "2",  # Pix Chave
            "termo_busca": "usuario@exemplo.com",  # Email como chave Pix
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert form.is_valid(), f"Erros: {form.errors}"

    def test_validacao_aplicada_tipo_3(self):
        """Testa se a validação é aplicada para tipo de requisição 3 (CCS CPF/CNPJ)."""
        form_data = {
            "tipo_requisicao": "3",  # CCS CPF/CNPJ
            "termo_busca": "11144477735",  # CPF válido
            "motivo": "Teste de validação",
        }
        form = RequisicaoBacenForm(data=form_data)
        assert form.is_valid(), f"Erros: {form.errors}"

    def test_help_text_termo_busca(self):
        """Testa se o help_text do campo termo_busca está correto."""
        form = RequisicaoBacenForm()
        expected_help_text = (
            "Para tipos Pix CPF/CNPJ e CCS CPF/CNPJ, informe um CPF (11 dígitos) "
            "ou CNPJ (14 dígitos) válido."
        )
        assert form.fields["termo_busca"].help_text == expected_help_text
