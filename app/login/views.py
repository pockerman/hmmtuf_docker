from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Create your views here.


def login_view(request):

    template = loader.get_template('login/login_view.html')
    context = {}

    print("INFO: login_view...")

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        post_next = request.POST.get('next')

        if not User.objects.filter(username=username).exists():
            context = {"error_msg": "Invalid user or password", 'next': post_next}
            return HttpResponse(template.render(context, request))

        user = authenticate(username=username, password=password)

        if user is not None:

            # attempt to login the user
            login(request=request, user=user)
            post_next = request.POST.get('next')

            if post_next == '/hmmtuf_login/login/':
                return redirect(to='/')

            return redirect(to=request.POST.get('next'))
        else:
            context = {"error_msg": "Invalid user or password", 'next': post_next}
            return HttpResponse(template.render(context, request))

    print("INFO: {0}".format(request.GET))
    # set the next field so that we redirect
    context['next'] = request.GET.get('next')
    return HttpResponse(template.render(context, request))
