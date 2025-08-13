from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from consultalab.bacen.filters import RequisicaoBacenFilter
from consultalab.bacen.forms import RequisicaoBacenFilterFormHelper
from consultalab.bacen.helpers import LIST_PAGE_SIZE
from consultalab.bacen.models import RequisicaoBacen


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"
    page_size = LIST_PAGE_SIZE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = RequisicaoBacen.objects.filter(user=self.request.user).order_by("-created")
        requisicao_filter = RequisicaoBacenFilter(self.request.GET, queryset=qs)

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

        context["requisicoes"] = requisicao_object
        context["requisicoes_filter_form"] = requisicao_filter_form
        context["requisicoes_total"] = requisicao_filter.qs.count()

        return context


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = "pages/about.html"
