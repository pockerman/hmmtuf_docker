from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


from webapp_utils.helpers import get_configuration
from hmmtuf.config import MEDIA_URL
from hmmtuf_home.models import HMMModel, RegionModel, RegionGroupTipModel
from compute_engine.src.utils import extract_file_names, extract_path
from compute_engine import OK
from compute_engine import ERROR
from .forms import ErrorHandler, RegionLoadForm


__all__ = ['load_hmm_json_view', 'load_region_view']


# Views

def success_load_view_hmm(request, hmm_name):
    template = loader.get_template('file_loader/load_success.html')
    return HttpResponse(template.render({'name': hmm_name, 'load_hmm': True, "MEDIA_URL": MEDIA_URL}, request))


def success_load_view_region(request, region_name):
    template = loader.get_template('file_loader/load_success.html')
    return HttpResponse(template.render({'name': region_name, 'load_region':True, "MEDIA_URL": MEDIA_URL}, request))


@login_required(login_url='/hmmtuf_login/login/')
def load_hmm_json_view(request):
    """
    The view for loading a JSON file describing
    an HMM
    """

    template = loader.get_template('file_loader/load_hmm_view.html')

    if request.method == 'POST':

        error_handler = ErrorHandler(filename="hmm_filename", item_name="hmm_name",
                                     template_html='file_loader/load_hmm_view.html')

        if error_handler.check(request=request) is not OK:
             return error_handler.response

        # check if the HMM model with such a name exists
        # if yes then we return an error
        try:
            model = HMMModel.objects.get(name=error_handler.name)
        except ObjectDoesNotExist:

            try:
                hmm_inst = HMMModel()
                hmm_inst = HMMModel.build_from_form(inst=hmm_inst,
                                                    form=error_handler, save=True)
                return redirect('success_load_view_hmm', hmm_name=hmm_inst.name)
            except Exception as e:
                print(f"{ERROR} DB_ERROR occurred {str(e)}")
                return HttpResponse(template.render({"error_found": f"DB ERROR {str(e)}"}, request))

        return HttpResponse(template.render({"error_found": f"The HMM name={error_handler.name} exists"}, request))

    template = loader.get_template('file_loader/load_hmm_view.html')
    return HttpResponse(template.render({"MEDIA_URL": MEDIA_URL}, request))


@login_required(login_url='/hmmtuf_login/login/')
def load_region_view(request):
    """
    The view for loading a region file
    """

    configuration = get_configuration()
    reference_files_names, wga_files_names, nwga_files_names = extract_file_names(configuration=configuration)
    path = extract_path(configuration=configuration, ref_file=reference_files_names[0])

    context = {"reference_files": reference_files_names,
               "wga_files": wga_files_names,
               "nwga_files": nwga_files_names,
               "MEDIA_URL": MEDIA_URL}

    if request.method == 'POST':

        error_handler = RegionLoadForm(filename="region_file", item_name="region_name",
                                       context=context, path=path,
                                       template_html='file_loader/load_region_view.html')

        if error_handler.check(request=request) is not OK:
            return error_handler.response

        # check if the region model with such a name exists
        # if yes then we return an error
        try:
            model = RegionModel.objects.get(name=error_handler.name)
        except ObjectDoesNotExist:

            # do we have the group tip or need to create it
            group_tip = error_handler.group_tip

            try:
                tip_model = RegionGroupTipModel.objects.get(tip=group_tip)
            except:
                tip_model = RegionGroupTipModel()
                tip_model.tip = group_tip
                tip_model.save()

            region_inst = RegionModel()
            region_inst.group_tip = tip_model
            region_inst = RegionModel.build_from_form(inst=region_inst,
                                                      form=error_handler, save=True)

            return redirect('success_load_view_region', region_name=region_inst.name)

        template = loader.get_template('file_loader/load_region_view.html')
        return HttpResponse(template.render({"error_name_exist": "The region name exists. Specify "
                                                                 "another name for the region"}, request))

    # if not post simply return the view
    template = loader.get_template('file_loader/load_region_view.html')
    return HttpResponse(template.render(context, request))

