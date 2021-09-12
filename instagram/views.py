from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
# Create your views here.
from instagram.forms import SignUpForm


def home(request):
    return render(request,'index.html')

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

def profile(request,id):
    return render(request, 'profile.html', locals())

    if request.method == 'POST':
        if 'that_user_id' in request.POST:
            that_user_id = request.POST.get('that_user_id')  # get user id
            that_user = User.objects.get(id=that_user_id)  # get that user

            my_profile = Profile.objects.get(user=request.user)  # my profile
            my_profile.following.add(that_user) # add them to my following
            my_profile.save()


            their_profile = Profile.objects.get(user=that_user)
            their_profile.followers.add(request.user) # add me to their followers
            their_profile.save()


    return render(request, 'profile.html', locals())
