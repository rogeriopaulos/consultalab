import time

import pytest
from celery.result import AsyncResult

from consultalab.bacen.models import ChavePix
from consultalab.bacen.models import RequisicaoBacen
from consultalab.bacen.tasks import request_bacen_pix

pytestmark = pytest.mark.django_db


@pytest.mark.integrations_test
def test_request_bacen_pix(settings, requisicao_bacen_cpf: RequisicaoBacen):
    task_result = request_bacen_pix.delay(requisicao_bacen_cpf.termo_busca)
    assert isinstance(task_result, AsyncResult)

    # Polling para aguardar o resultado da task
    timeout = 30  # Tempo limite em segundos
    interval = 1  # Intervalo entre verificações
    elapsed_time = 0
    while not task_result.ready() and elapsed_time < timeout:
        time.sleep(interval)
        elapsed_time += interval
    assert task_result.ready(), "A task não foi concluída dentro do tempo limite"

    chave = ChavePix.objects.filter(
        requisicao_bacen=requisicao_bacen_cpf,
        cpf_cnpj=requisicao_bacen_cpf.termo_busca,
    ).first()
    assert chave is not None, "Chave não encontrada no banco de dados"
