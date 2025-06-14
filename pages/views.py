from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'pages/index.html')

def Explore_Courses(request): 
    return render(request, 'pages/Explore_Courses.html')

def Featured_Instructors(request): 
    return render(request, 'pages/Featured_Instructors.html')

def Learning_Path(request): 
    return render(request, 'pages/learning_path.html')