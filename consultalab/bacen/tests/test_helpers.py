import pytest
from django.conf import settings

from consultalab.bacen.api import BacenRequestApi
from consultalab.bacen.helpers import camelcase_to_snake_case


class TestBacenRequestApi:
    request_api = BacenRequestApi()

    @pytest.mark.integrations_test
    def test_get_pix_by_cpf(self):
        response = self.request_api.get_pix_by_cpf_cnpj(
            settings.BACEN_API_DICT_CPF_TEST,
            "Consulta de vinculo",
        )

        assert isinstance(response, dict)
        assert "data" in response
        assert len(response["data"]) > 0

    @pytest.mark.integrations_test
    def test_get_pix_by_cnpj(self):
        response = self.request_api.get_pix_by_cpf_cnpj(
            settings.BACEN_API_DICT_CNPJ_TEST,
            "Consulta de vinculo",
        )

        assert isinstance(response, dict)
        assert "data" in response
        assert len(response["data"]) > 0


def test_camelcase_to_snake_case():
    data = {
        "chave": "12345678900",
        "nome": "João da Silva",
        "tipoPessoa": "FISICA",
        "dataHoraVinculo": "2023-01-01T00:00:00Z",
        "instituicao": {
            "nomeBanco": "Banco do Brasil",
            "codigoBanco": 1,
        },
    }

    snake_case_data = camelcase_to_snake_case(data)
    assert isinstance(snake_case_data, dict)
    assert "tipo_pessoa" in snake_case_data
    assert "data_hora_vinculo" in snake_case_data

    snake_case_data_instituicao = camelcase_to_snake_case(data["instituicao"])
    assert isinstance(snake_case_data_instituicao, dict)
    assert "nome_banco" in snake_case_data_instituicao
    assert "codigo_banco" in snake_case_data_instituicao
