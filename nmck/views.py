from django.views.generic import FormView
from django.http.response import FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import NmckPositionFormSet
from .utils import work_with_excel


class CreateNmckView(LoginRequiredMixin, FormView):
    """
    Форма создания и редактирования НМЦК
    """
    form_class = NmckPositionFormSet
    template_name = 'nmck/create.html'

    def post(self, request, *args, **kwargs):
        """
        Проверяет правильность формы и в случае успеха рендерит файл с расчетом
        """
        form = self.get_form()
        if form.is_valid():
            file = work_with_excel.render_table(
                form.cleaned_data, request.user.last_name
            )
            response = FileResponse(
                file,
                content_type='application/vnd.openxmlformats-officedocument.'
                             'spreadsheetml.sheet'
            )
            response['Content-Disposition'] = (
                'attachment; filename=NMCK.xlsx'
            )
        else:
            response = self.get(request)
            response.context_data['form'] = form
        return response
