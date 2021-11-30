import json
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from compute_engine.src.constants import OK
from compute_engine.src.hmm_builder import create_hmm_model_from_form

from webapp_utils.helpers import make_hmm_file_path
from hmmtuf_home.models import HMMModel
from .forms import HMMFormCreator


def success_create_hmm_view(request, hmm_name):
    template = loader.get_template('hmm_creator/success_create_hmm_view.html')
    context={"hmm_name": hmm_name}
    return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def create_hmm_view(request):

    context = {}
    if request.method == 'POST':

        form = HMMFormCreator(template='hmm_creator/create_hmm_view.html',
                              context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        hmm_model = create_hmm_model_from_form(form=form)
        json_str = hmm_model.to_json()
        filename = make_hmm_file_path(hmm_name=form.hmm_name + ".json")

        with open(filename, 'w') as jsonfile:
            json.dump(json_str, jsonfile)

            hmm_model_obj = HMMModel()
            hmm_model_obj.name = form.hmm_name
            hmm_model_obj.file_hmm = filename
            hmm_model_obj.extension = 'json'
            hmm_model_obj.save()

        return redirect('success_create_hmm_view', hmm_name=form.hmm_name)

    template = loader.get_template('hmm_creator/create_hmm_view.html')
    return HttpResponse(template.render(context, request))

