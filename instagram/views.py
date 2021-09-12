from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from instagram.forms import SignUpForm
from instagram.models import Profile, Image


def home(request):
    images=Image.objects.all()
    return render(request, 'index.html',{'images':images})


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
    profile = Profile.objects.get(id=id)

    if request.method == 'POST':
        if 'that_user_id' in request.POST:
            that_user_id = request.POST.get('that_user_id') # get user id
            that_user = User.objects.get(id=that_user_id) # get that user

            my_profile = Profile.objects.get(user=request.user) # my profile
            my_profile.following.add(that_user) # add them to my following
            my_profile.save()

            their_profile = Profile.objects.get(user=that_user)
            their_profile.followers.add(request.user) # add me to their followers
            their_profile.save()

    return render(request, 'profile.html', locals())


def search_results(request):
    if 'category' in request.GET and request.GET["category"]:
        search_category = request.GET.get("category")

        searched_category_images = Image.search_by_category(search_category)
        print(searched_category_images)
        message = f"{search_category}"

        return render(request, 'search.html',locals())

    else:
        message = "No such word"
        return render(request, 'search.html',{"message":message})