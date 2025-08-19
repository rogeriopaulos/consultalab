import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase

from consultalab.bacen.forms import BulkRequestForm

User = get_user_model()

# Constantes para testes
EXPECTED_VALID_COUNT = 2
EXPECTED_INVALID_COUNT = 2


class BulkRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            name="Test User",
        )
        # Adiciona permissão para requisições Pix
        from django.contrib.auth.models import Permission

        permission = Permission.objects.get(codename="can_request_pix")
        self.user.user_permissions.add(permission)

    def test_valid_txt_file(self):
        """Testa upload de arquivo TXT válido"""
        content = "1,12345678901,BO 123/2023,REF001\n2,usuario@email.com,IPL 456/2023"

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            assert form.is_valid()

    def test_invalid_file_extension(self):
        """Testa arquivo com extensão inválida"""
        content = "1,12345678901,BO 123/2023"

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            assert not form.is_valid()
            assert "arquivo_txt" in form.errors

    def test_process_file_valid_lines(self):
        """Testa processamento de arquivo com linhas válidas"""
        content = "1,12345678901,BO 123/2023,REF001\n2,usuario@email.com,IPL 456/2023"

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            if form.is_valid():
                validas, invalidas = form.process_file(self.user)

                assert len(validas) == EXPECTED_VALID_COUNT
                assert len(invalidas) == 0

                # Verifica primeira linha
                assert validas[0]["tipo_requisicao"] == "1"
                assert validas[0]["termo_busca"] == "12345678901"
                assert validas[0]["motivo"] == "BO 123/2023"
                assert validas[0]["referencia"] == "REF001"

                # Verifica segunda linha
                assert validas[1]["tipo_requisicao"] == "2"
                assert validas[1]["termo_busca"] == "usuario@email.com"
                assert validas[1]["motivo"] == "IPL 456/2023"
                assert validas[1]["referencia"] == ""

    def test_process_file_invalid_cpf(self):
        """Testa processamento de arquivo com CPF inválido"""
        content = "1,12345678900,BO 123/2023"  # CPF inválido

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            if form.is_valid():
                validas, invalidas = form.process_file(self.user)

                assert len(validas) == 0
                assert len(invalidas) == 1
                assert "CPF inválido" in invalidas[0]["erro"]

    def test_process_file_insufficient_fields(self):
        """Testa processamento de arquivo com campos insuficientes"""
        content = "1,12345678901"  # Falta motivo

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            if form.is_valid():
                validas, invalidas = form.process_file(self.user)

                assert len(validas) == 0
                assert len(invalidas) == 1
                assert "pelo menos 3 campos" in invalidas[0]["erro"]

    def test_process_file_invalid_tipo_requisicao(self):
        """Testa processamento de arquivo com tipo de requisição inválido"""
        content = "3,12345678901,BO 123/2023"  # Tipo 3 não permitido

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            if form.is_valid():
                validas, invalidas = form.process_file(self.user)

                assert len(validas) == 0
                assert len(invalidas) == 1
                assert "tipo_requisicao deve ser 1" in invalidas[0]["erro"]

    def test_process_file_mixed_valid_invalid(self):
        """Testa processamento de arquivo com linhas válidas e inválidas"""
        content = (
            "1,12345678901,BO 123/2023,REF001\n"  # Válida
            "1,12345678900,BO 124/2023\n"  # CPF inválido
            "2,usuario@email.com,IPL 456/2023\n"  # Válida
            "3,12345678901,BO 125/2023"  # Tipo inválido
        )

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write(content)
            f.seek(0)

            form_data = {}
            file_data = {"arquivo_txt": f}
            form = BulkRequestForm(form_data, file_data)

            if form.is_valid():
                validas, invalidas = form.process_file(self.user)

                assert len(validas) == EXPECTED_VALID_COUNT
                assert len(invalidas) == EXPECTED_INVALID_COUNT
