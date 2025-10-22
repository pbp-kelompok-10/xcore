from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.
def landing_home(request):
    context = {
        'title': 'Welcome to Xcore',
        'tagline': 'Web scoring terbaik cihuyyyyyyy',
        'features': [
            'Scoreboard',
            'Statistic', 
            'Highlight',
            'Prediction',
        ]
    }
    return render(request, 'landing.html', context)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('landingpage:home')
    context = {'form':form}
    return render(request, 'register.html', context)


