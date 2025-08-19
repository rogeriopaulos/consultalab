import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db import transaction
from django.http import FileResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import View

from consultalab.bacen.enhanced_report import EnhancedPixReportGenerator
from consultalab.bacen.filters import RequisicaoBacenFilter
from consultalab.bacen.forms import BulkRequestForm
from consultalab.bacen.forms import RequisicaoBacenFilterFormHelper
from consultalab.bacen.forms import RequisicaoBacenForm
from consultalab.bacen.helpers import LIST_PAGE_SIZE
from consultalab.bacen.models import RequisicaoBacen
from consultalab.bacen.report_forms import ReportTypeForm
from consultalab.bacen.tasks import request_bacen_pix

logger = logging.getLogger(__name__)


class CPFCNPJFormView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = RequisicaoBacenForm(initial={"tipo_requisicao": "1"})
        return render(
            request,
            "bacen/partials/pix_modal.html",
            {"form": form, "tipo_requisicao": "1"},
        )


class ChavePixFormView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = RequisicaoBacenForm(initial={"tipo_requisicao": "2"})
        return render(
            request,
            "bacen/partials/pix_modal.html",
            {"form": form, "tipo_requisicao": "2"},
        )


class RequisicaoBacenCreateView(LoginRequiredMixin, CreateView):
    model = RequisicaoBacen
    form_class = RequisicaoBacenForm
    template_name = "pages/home.html"
    success_url = reverse_lazy("core:home")
    success_message = "Requisição Bacen criada com sucesso!"
    page_size = LIST_PAGE_SIZE

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user

        if form.instance.tipo_requisicao in ["1", "2"] and not user.has_perm(
            "users.can_request_pix",
        ):
            form.add_error(None, "Usuário não autorizado a realizar requisições Pix.")
            return self.form_invalid(form)

        if form.instance.tipo_requisicao == "3" and not user.has_perm(
            "users.can_request_ccs",
        ):
            form.add_error(None, "Usuário não autorizado a realizar requisições CCS.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        requisicoes = RequisicaoBacen.objects.filter(user=self.request.user).order_by(
            "-created",
        )
        requisicao_filter = RequisicaoBacenFilter(
            self.request.GET,
            queryset=requisicoes,
        )

        requisicao_filter.form.helper = RequisicaoBacenFilterFormHelper()
        requisicao_filter_form = requisicao_filter.form
        requisicao_filter_qs = requisicao_filter.qs

        paginator = Paginator(requisicao_filter_qs, self.page_size)
        page_number = self.request.GET.get("page")
        try:
            requisicao_object = paginator.page(page_number)
        except PageNotAnInteger:
            requisicao_object = paginator.page(1)
        except EmptyPage:
            requisicao_object = paginator.page(paginator.num_pages)

        response.context_data["requisicoes"] = requisicao_object
        response.context_data["requisicoes_filter_form"] = requisicao_filter_form
        response.context_data["messages_toast"] = form.errors["__all__"]
        return response


class ProcessarRequisicaoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        requisicao_id = kwargs.get("requisicao_id")
        requisicao = RequisicaoBacen.objects.get(id=requisicao_id)

        task = request_bacen_pix.delay(requisicao.id)
        requisicao.task_id = task.id
        requisicao.processada = True
        requisicao.save()

        return render(
            request,
            "bacen/partials/requisicao_row.html",
            {"requisicao": requisicao},
        )


class RequisicaoBacenStatusView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requisicao_id = kwargs.get("requisicao_id")
        requisicao = RequisicaoBacen.objects.get(id=requisicao_id)

        if requisicao.get_status()["finished"]:
            response = render(
                request,
                "bacen/partials/requisicao_row_status.html",
                {"requisicao": requisicao},
            )
            response.status_code = 286
            return response

        return render(
            request,
            "bacen/partials/requisicao_row_status.html",
            {"requisicao": requisicao},
        )


class RequisicaoBacenDetailView(LoginRequiredMixin, DetailView):
    model = RequisicaoBacen
    template_name = "bacen/partials/requisicao_bacen_detail.html"
    context_object_name = "requisicao"

    def get_queryset(self):
        return RequisicaoBacen.objects.prefetch_related("chaves_pix").filter(
            user=self.request.user,
        )


class ReportTypeModalView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requisicao_id = kwargs.get("requisicao_id")

        try:
            requisicao = RequisicaoBacen.objects.get(
                id=requisicao_id,
                user=request.user,
            )
        except RequisicaoBacen.DoesNotExist:
            return HttpResponseForbidden("Requisição não encontrada ou acesso negado.")

        form = ReportTypeForm()

        return render(
            request,
            "bacen/partials/report_type_modal.html",
            {"requisicao": requisicao, "form": form},
        )


class RequisicaoBacenPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requisicao_id = kwargs.get("requisicao_id")
        requisicao = RequisicaoBacen.objects.get(id=requisicao_id)

        # Verificar se o usuário tem permissão para acessar esta requisição
        if requisicao.user != request.user:
            return HttpResponseForbidden("Acesso negado.")

        # Obter o tipo de relatório da query string (padrão: detailed)
        report_type = request.GET.get("report_type", "detailed")

        # Validar o tipo de relatório
        if report_type not in ["summary", "detailed"]:
            report_type = "detailed"

        # Usar o gerador aprimorado
        report_generator = EnhancedPixReportGenerator(report_type=report_type)
        data = requisicao.to_dict()
        buffer = report_generator.generate_report(
            data["requisicao_data"],
            data["chaves_pix"],
        )

        # Nome do arquivo baseado no tipo de relatório
        filename_suffix = "resumido" if report_type == "summary" else "detalhado"

        criado_em = data["requisicao_data"]["criado_em"]
        if criado_em is not None:
            created_at = criado_em.strftime("%Y%m%d")
        else:
            created_at = "unknown"
        term = slugify(data["requisicao_data"]["termo_busca"])
        filename = f"relatorio_{filename_suffix}_{created_at}_{term}.pdf"

        return FileResponse(buffer, as_attachment=True, filename=filename)


class RequisicaoBacenDeleteView(LoginRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        requisicao_id = kwargs.get("requisicao_id")
        response = render(
            request,
            "bacen/partials/empty_content.html",
            {"requisicao": None},
        )
        has_error = False

        try:
            requisicao = RequisicaoBacen.objects.get(id=requisicao_id)
            if requisicao.user == request.user:
                requisicao.delete()
                response.status_code = 200
                return response
            msg = "Usuário não autorizado a excluir esta requisição Bacen."
            logger.error(msg)
            has_error = True
        except RequisicaoBacen.DoesNotExist:
            msg = "Requisição Bacen não encontrada ou não pertence ao usuário."
            logger.exception(msg)
            has_error = True

        if has_error:
            response["HX-Trigger"] = f'{{"showMessage": "{msg}"}}'
            response.status_code = 400
        return response


class ReferenciaFormView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requisicao = RequisicaoBacen.objects.get(id=kwargs.get("pk"))
        return render(
            request,
            "bacen/partials/referencia_form.html",
            {
                "requisicao_id": kwargs.get("pk"),
                "referencia": requisicao.referencia,
            },
        )


class RequisicaoBacenRowView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requisicao = RequisicaoBacen.objects.get(id=kwargs.get("requisicao_id"))
        return render(
            request,
            "bacen/partials/requisicao_row.html",
            {"requisicao": requisicao},
        )


class UpdateReferenciaView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        requisicao = RequisicaoBacen.objects.get(id=kwargs.get("requisicao_id"))
        referencia = request.POST.get("referencia")
        delete_param = request.GET.get("delete", "false")

        if delete_param == "true":
            requisicao.referencia = ""
            requisicao.save()
            return render(
                request,
                "bacen/partials/requisicao_row.html",
                {"requisicao": requisicao},
            )

        if not referencia:
            response = render(
                request,
                "bacen/partials/requisicao_row.html",
                {"requisicao": requisicao},
            )
            response["HX-Trigger"] = '{"showMessage": "Referência não pode ser vazia."}'
            response.status_code = 400
            return response

        requisicao.referencia = referencia
        requisicao.save()

        return render(
            request,
            "bacen/partials/referencia_success.html",
            {
                "referencia": referencia,
                "requisicao_id": requisicao.id,
            },
        )


class BulkRequestFormView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = BulkRequestForm()
        return render(
            request,
            "bacen/partials/bulk_request_modal.html",
            {"form": form},
        )


class BulkRequestUploadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = BulkRequestForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                requisicoes_validas, requisicoes_invalidas = form.process_file(
                    request.user,
                )

                # Salva as requisições válidas no banco de dados
                requisicoes_criadas = []
                with transaction.atomic():
                    for req_data in requisicoes_validas:
                        requisicao = RequisicaoBacen.objects.create(**req_data)
                        requisicoes_criadas.append(requisicao)

                # Prepara dados para o template de resultado
                resultado = {
                    "total_linhas": len(requisicoes_validas)
                    + len(requisicoes_invalidas),
                    "requisicoes_validas": len(requisicoes_validas),
                    "requisicoes_invalidas": len(requisicoes_invalidas),
                    "requisicoes_criadas": requisicoes_criadas,
                    "erros": requisicoes_invalidas,
                }

                return render(
                    request,
                    "bacen/partials/bulk_request_result.html",
                    {"resultado": resultado},
                )

            except (ValueError, TypeError, AttributeError) as e:
                form.add_error("arquivo_txt", f"Erro ao processar arquivo: {e!s}")

        return render(
            request,
            "bacen/partials/bulk_request_modal.html",
            {"form": form},
        )
