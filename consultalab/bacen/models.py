from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.contrib.auth import get_user_model
from django.db import models
from django_celery_results.models import TaskResult

from consultalab.bacen.helpers import has_object
from consultalab.core.models import AppModel

User = get_user_model()


class RequisicaoBacen(AppModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="requisicoes_bacen",
        verbose_name="Usuário",
    )
    TIPO_REQUISICAO_CHOICES = [
        ("1", "Pix CPF/CNPJ"),
        ("2", "Pix Chave"),
        ("3", "CCS CPF/CNPJ"),
    ]
    tipo_requisicao = models.CharField(
        max_length=1,
        choices=TIPO_REQUISICAO_CHOICES,
        verbose_name="Tipo de Requisição",
        db_column="tipo_requisicao",
    )
    termo_busca = models.CharField(
        max_length=255,
        verbose_name="Termo de Busca",
        db_column="termo_busca",
        blank=True,
    )
    motivo = models.CharField(
        max_length=255,
        verbose_name="Motivo",
        db_column="motivo",
        blank=True,
    )
    processada = models.BooleanField(
        default=False,
        verbose_name="Requisição processada",
        db_column="processada",
    )
    task_id = models.CharField(
        max_length=255,
        verbose_name="ID da Tarefa",
        db_column="task_id",
        blank=True,
    )
    referencia = models.CharField(
        max_length=255,
        verbose_name="Referência",
        db_column="referencia",
        blank=True,
    )

    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Requisição Bacen"
        verbose_name_plural = "Requisições Bacen"
        db_table = "REQUISICOES_BACEN"

    def __str__(self):
        return f"Requisição {self.tipo_requisicao} | {self.user} | {self.created}"

    def get_status(self):
        task_status = {
            "PENDING": {
                "text": "Pendente",
                "icon": "bi bi-exclamation-triangle",
                "class": "text-bg-warning",
                "finished": False,
            },
            "SUCCESS": {
                "text": "Analisado",
                "icon": "bi bi-check",
                "class": "text-bg-success",
                "finished": True,
            },
            "FAILURE": {
                "text": "Falhou",
                "icon": "bi bi-x",
                "class": "text-bg-danger",
                "finished": True,
            },
            "RECEIVED": {
                "text": "Recebido",
                "icon": "bi bi-info-circle",
                "class": "text-bg-info",
                "finished": False,
            },
            "RETRY": {
                "text": "Nova tentativa",
                "icon": "bi bi-arrow-clockwise",
                "class": "text-bg-secondary",
                "finished": False,
            },
            "REVOKED": {
                "text": "Descartado",
                "icon": "bi bi-trash",
                "class": "text-bg-dark",
                "finished": True,
            },
            "STARTED": {
                "text": "Iniciado",
                "icon": "bi bi-play",
                "class": "text-bg-info",
                "finished": False,
            },
        }
        if has_object(TaskResult, task_id=self.task_id):
            task_result = TaskResult.objects.get(task_id=self.task_id)
            return task_status[task_result.status]

        return {"text": "Aguardando", "icon": "bi bi-clock-history", "finished": False}

    def to_dict(self):
        requisicao_data = {
            "termo_busca": self.termo_busca,
            "tipo_requisicao": self.get_tipo_requisicao_display(),
            "motivo": self.motivo,
            "processada": self.processada,
            "status": self.get_status(),
            "criado_em": self.created,
            "responsavel": self.user.name,
        }

        chaves_pix = self.chaves_pix.all()

        return {
            "requisicao_data": requisicao_data,
            "chaves_pix": [chave.to_dict() for chave in chaves_pix],
        }


class ChavePix(AppModel):
    requisicao_bacen = models.ForeignKey(
        RequisicaoBacen,
        on_delete=models.CASCADE,
        related_name="chaves_pix",
        verbose_name="Requisição Bacen",
    )
    chave = models.CharField(
        max_length=255,
        verbose_name="Chave",
        db_column="chave",
        blank=True,
    )
    tipo_chave = models.CharField(
        max_length=50,
        verbose_name="Tipo de Chave",
        db_column="tipo_chave",
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Status",
        db_column="status",
        blank=True,
    )
    data_abertura_reivindicacao = models.DateTimeField(
        verbose_name="Data Abertura Reivindicação",
        db_column="data_abertura_reivindicacao",
        blank=True,
        null=True,
    )
    cpf_cnpj = models.CharField(
        max_length=50,
        verbose_name="CPF/CNPJ",
        db_column="cpf_cnpj",
        blank=True,
    )
    nome_proprietario = models.CharField(
        max_length=255,
        verbose_name="Nome Proprietário",
        db_column="nome_proprietario",
        blank=True,
    )
    nome_fantasia = models.CharField(
        max_length=255,
        verbose_name="Nome Fantasia",
        db_column="nome_fantasia",
        blank=True,
    )
    participante = models.JSONField(
        verbose_name="Participante",
        db_column="participante",
        blank=True,
        null=True,
    )
    agencia = models.CharField(
        max_length=50,
        verbose_name="Agência",
        db_column="agencia",
        blank=True,
    )
    numero_conta = models.CharField(
        max_length=50,
        verbose_name="Número da Conta",
        db_column="numero_conta",
        blank=True,
    )
    tipo_conta = models.CharField(
        max_length=50,
        verbose_name="Tipo da Conta",
        db_column="tipo_conta",
        blank=True,
    )
    data_abertura_conta = models.DateTimeField(
        verbose_name="Data Abertura da Conta",
        db_column="data_abertura_conta",
        blank=True,
        null=True,
    )
    proprietario_da_chave_desde = models.DateTimeField(
        verbose_name="Proprietário da Chave Desde",
        db_column="proprietario_da_chave_desde",
        blank=True,
        null=True,
    )
    data_criacao = models.DateTimeField(
        verbose_name="Data Criação",
        db_column="data_criacao",
        blank=True,
        null=True,
    )
    ultima_modificacao = models.DateTimeField(
        verbose_name="Última Modificação",
        db_column="ultima_modificacao",
        blank=True,
        null=True,
    )

    banco = models.CharField(
        max_length=255,
        verbose_name="Banco",
        default="Desconhecido",
        db_column="banco",
        blank=True,
    )

    class Meta:
        verbose_name = "Chave Pix"
        verbose_name_plural = "Chaves Pix"
        db_table = "CHAVES_PIX"

    def __str__(self):
        return (
            f"Chave Pix - {self.chave} | {self.requisicao_bacen.user} | {self.created}"
        )

    def to_dict(self):
        eventos_vinculo = self.eventos_vinculo.all()

        return {
            "chave": self.chave,
            "tipo_chave": self.tipo_chave,
            "status": self.status,
            "cpf_cnpj": self.cpf_cnpj,
            "nome_proprietario": self.nome_proprietario,
            "nome_fantasia": self.nome_fantasia,
            "participante": self.participante,
            "agencia": self.agencia,
            "numero_conta": self.numero_conta,
            "tipo_conta": self.tipo_conta,
            "eventos_vinculo": [evento.to_dict() for evento in eventos_vinculo],
            "data_abertura_conta": self.data_abertura_conta,
            "banco": self.get_bank_label(),
        }

    def get_bank_label(self):
        if not self.participante:
            return "Desconhecido"

        nome = self.participante.get("nome", "")
        cod = self.participante.get("codigoCompensacao", "")
        if nome and cod:
            return f"{cod} {nome}"

        if nome:
            return nome

        return "Desconhecido"


class EventoVinculo(AppModel):
    chave_pix = models.ForeignKey(
        ChavePix,
        on_delete=models.CASCADE,
        related_name="eventos_vinculo",
        verbose_name="Chave Pix",
    )
    tipo_evento = models.CharField(
        max_length=255,
        verbose_name="Tipo do Evento",
        db_column="tipo_evento",
        blank=True,
    )
    motivo_evento = models.CharField(
        max_length=255,
        verbose_name="Motivo do Evento",
        db_column="motivo_evento",
        blank=True,
    )
    data_evento = models.DateTimeField(
        verbose_name="Data do Evento",
        db_column="data_evento",
        blank=True,
        null=True,
    )
    chave = models.CharField(
        max_length=255,
        verbose_name="Chave",
        db_column="chave",
        blank=True,
    )
    tipo_chave = models.CharField(
        max_length=255,
        verbose_name="Tipo da Chave",
        db_column="tipo_chave",
        blank=True,
    )
    cpf_cnpj = models.CharField(
        max_length=255,
        verbose_name="CPF/CNPJ",
        db_column="cpf_cnpj",
        blank=True,
    )
    nome_proprietario = models.CharField(
        max_length=255,
        verbose_name="Nome do Proprietário",
        db_column="nome_proprietario",
        blank=True,
    )
    nome_fantasia = models.CharField(
        max_length=255,
        verbose_name="Nome Fantasia",
        db_column="nome_fantasia",
        blank=True,
    )
    participante = models.JSONField(
        verbose_name="Participante",
        db_column="participante",
        blank=True,
        null=True,
    )
    agencia = models.CharField(
        max_length=50,
        verbose_name="Agência",
        db_column="agencia",
        blank=True,
    )
    numero_conta = models.CharField(
        max_length=50,
        verbose_name="Número da Conta",
        db_column="numero_conta",
        blank=True,
    )
    tipo_conta = models.CharField(
        max_length=50,
        verbose_name="Tipo da Conta",
        db_column="tipo_conta",
        blank=True,
    )
    data_abertura_conta = models.DateTimeField(
        verbose_name="Data Abertura da Conta",
        db_column="data_abertura_conta",
        blank=True,
        null=True,
    )
    banco = models.CharField(
        max_length=255,
        verbose_name="Banco",
        default="Desconhecido",
        db_column="banco",
        blank=True,
    )

    class Meta:
        verbose_name = "Evento Vinculo Pix CPF/CNPJ"
        verbose_name_plural = "Eventos Vinculo Pix CPF/CNPJ"
        db_table = "EVENTOS_VINCULO_PIX"

    def __str__(self):
        return f"Evento Vinculo - {self.chave_pix} | Tipo: {self.tipo_evento}"

    def to_dict(self):
        return {
            "tipo_evento": self.tipo_evento,
            "motivo_evento": self.motivo_evento,
            "data_evento": self.data_evento,
            "chave": self.chave,
            "tipo_chave": self.tipo_chave,
            "cpf_cnpj": self.cpf_cnpj,
            "nome_proprietario": self.nome_proprietario,
            "nome_fantasia": self.nome_fantasia,
            "participante": self.participante,
            "agencia": self.agencia,
            "numero_conta": self.numero_conta,
            "tipo_conta": self.tipo_conta,
            "data_abertura_conta": self.data_abertura_conta,
            "banco": self.get_bank_label(),
        }

    def get_bank_label(self):
        if not self.participante:
            return "Desconhecido"

        nome = self.participante.get("nome", None)
        cod = self.participante.get("codigoCompensacao", "")
        if nome and cod:
            return f"{cod} {nome}"

        if nome:
            return nome

        return "Desconhecido"


# Auditlog registries
# ------------------------------------------------------------------------------
auditlog.register(RequisicaoBacen)
