from django.shortcuts import redirect,render
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from .models import  *

def signup(request):
    '''View function that signs up a new user'''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, "Your user account has been successfully created.")
            return redirect(reverse('homepage'))
    else:
        form = SignUpForm()
        
    title = 'Create New Account'
    context={
        'title': title,
        'form': form,
        }
    return render(request, 'registration/signup.html', context)

def homepage(request):
    return render(request, 'homepage.html')

#PROFILE LOGIC
class ProfileDetailView(generic.DetailView):
    model = Profile
    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        return context
    
class ProfileUpdateView(LoginRequiredMixin ,generic.UpdateView):
    login_url='/login/'
    model = Profile
  
    fields = [
        "profile_photo",
        "bio",
        "phone_number"
    ]