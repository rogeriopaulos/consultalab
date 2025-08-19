from django.urls import path

from consultalab.bacen import views

app_name = "bacen"
urlpatterns = [
    path(
        "requisicao/",
        views.RequisicaoBacenCreateView.as_view(),
        name="requisicao_bacen",
    ),
    path(
        "requisicao/<int:requisicao_id>/relatorio/",
        views.RequisicaoBacenPDFView.as_view(),
        name="requisicao_bacen_relatorio",
    ),
    path(
        "requisicao/<int:requisicao_id>/remover/",
        views.RequisicaoBacenDeleteView.as_view(),
        name="requisicao_bacen_remover",
    ),
    path(
        "requisicao/<int:requisicao_id>/adicionar-referencia/",
        views.UpdateReferenciaView.as_view(),
        name="requisicao_bacen_referencia",
    ),
]
htmx_urlpatterns = [
    path("cpf_cnpj/", views.CPFCNPJFormView.as_view(), name="cpf_cnpj"),
    path("chave/", views.ChavePixFormView.as_view(), name="chave"),
    path(
        "processar-requisicao/<int:requisicao_id>/",
        views.ProcessarRequisicaoView.as_view(),
        name="processar_requisicao",
    ),
    path(
        "requisicao/<int:requisicao_id>/status/",
        views.RequisicaoBacenStatusView.as_view(),
        name="requisicao_status",
    ),
    path(
        "requisicao/<int:pk>/referencia/",
        views.ReferenciaFormView.as_view(),
        name="requisicao_bacen_referencia_form",
    ),
    path(
        "requisicao/<int:requisicao_id>/row/",
        views.RequisicaoBacenRowView.as_view(),
        name="requisicao_bacen_row",
    ),
    path(
        "requisicao/<int:pk>/",
        views.RequisicaoBacenDetailView.as_view(),
        name="requisicao_bacen_detail",
    ),
    path(
        "requisicao/<int:requisicao_id>/relatorio/modal/",
        views.ReportTypeModalView.as_view(),
        name="requisicao_bacen_relatorio_modal",
    ),
    path(
        "bulk-request/",
        views.BulkRequestFormView.as_view(),
        name="bulk_request_form",
    ),
    path(
        "bulk-request/upload/",
        views.BulkRequestUploadView.as_view(),
        name="bulk_request_upload",
    ),
]

urlpatterns += htmx_urlpatterns
