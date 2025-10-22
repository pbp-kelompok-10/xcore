from django.shortcuts import render

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
