from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView

from instagram.forms import SignUpForm
from instagram.models import Profile, Image, Comment
from django.contrib.auth.decorators import login_required

from project import settings


def home(request):
    if not request.user.is_authenticated:
        messages.info(request, 'you must be logged in')
        return redirect('signin')
    posts = Image.objects.all().order_by('-created_at')
    return render(request, 'index.html', locals())


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def profile(request, id):
    profile_user = User.objects.get(id=id)
    profile = Profile.objects.get(user=profile_user)
    posts = Image.objects.filter(profile=profile).order_by('-created_at')

    if request.method == 'POST':
        if 'that_user_id' in request.POST:
            that_user_id = request.POST.get('that_user_id')  # get user id
            that_user = User.objects.get(id=that_user_id)  # get that user

            my_profile = Profile.objects.get(user=request.user)  # my profile
            my_profile.following.add(that_user)  # add them to my following
            my_profile.save()

            their_profile = Profile.objects.get(user=that_user)
            their_profile.followers.add(request.user)  # add me to their followers
            their_profile.save()
            return HttpResponseRedirect(request.path_info)

        if 'post-image' in request.FILES and 'post-caption' in request.POST:
            post_image = request.FILES.get('post-image')
            post_caption = request.POST.get('post-caption')
            new_post = Image.objects.create(image=post_image, caption=post_caption, profile=profile)
            new_post.save()
            return HttpResponseRedirect(request.path_info)

        if 'post_comment' in request.POST and 'post_id' in request.POST:
            post_id = int(request.POST['post_id'])
            post = Image.objects.get(id=post_id)
            post_comment = request.POST.get('post_comment')
            post_user = request.user
            post_profile = Profile.objects.get(user=post_user)
            new_comment = Comment.objects.create(profile=post_profile, comment=post_comment)
            new_comment.save()
            post.comment.add(new_comment)
            post.save()
            return HttpResponseRedirect(request.path_info)


    return render(request, 'profile.html', locals())


def search_results(request):
    if 'category' in request.GET and request.GET["category"]:
        search_category = request.GET.get("category")

        searched_category_images = Image.search_by_category(search_category)
        print(searched_category_images)
        message = f"{search_category}"

        return render(request, 'search.html', locals())

    else:
        message = "No such word"
        return render(request, 'search.html', {"message": message})


def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    return JsonResponse(locals())


class LoginView(SuccessURLAllowedHostsMixin, FormView):
    """
    Display the login form and handle the login action.
    """
    form_class = AuthenticationForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'registration/login.html'
    redirect_authenticated_user = False
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return redirect('profile', id=form.get_user().id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'site': current_site,
            'site_name': current_site.name,
            **(self.extra_context or {})
        })
        return context


def post_likes(request):
    returned_data = {}
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Image.objects.get(id=post_id)
        our_user = request.user
        our_user_id = our_user.id
        if not our_user_id in post.likes:
            post.likes.append(our_user_id)
            post.save()
        returned_data['likes'] = len(post.likes)

    return JsonResponse(returned_data)


def view_post(request,id):
    post = Image.objects.get(id=id)

    if request.method == 'POST':
        if 'post_comment' in request.POST:
            post_comment = request.POST.get('post_comment')
            post_user = request.user
            post_profile = Profile.objects.get(user=post_user)
            new_comment = Comment.objects.create(profile=post_profile, comment = post_comment)
            new_comment.save()
            post.comment.add(new_comment)
            post.save()
            return HttpResponseRedirect(request.path_info)
    return render(request, 'view_post.html', locals())
