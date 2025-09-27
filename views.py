from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Job, SavedJob, JobAlert  # Ensure Job, SavedJob, and JobAlert models exist in models.py
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

def home(request):
    jobs = Job.objects.all()  # Fetch all jobs from the database
    return render(request, 'jobs/home.html')  # Render the home page template



def register(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            messages.success(request, "Registration successful!")
            return redirect('job_list')  # Redirect to job listings after registration
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def job_list(request):
    # Retrieve all jobs initially
    jobs = Job.objects.all().order_by('-date_posted')  # Ensure `date_posted` exists in the Job model

    # Get search query and filter parameters from the request
    title_query = request.GET.get('title', '')
    location_query = request.GET.get('location', '')
    job_type_query = request.GET.get('job_type', '')

    # Filter jobs based on user input
    if title_query:
        jobs = jobs.filter(title__icontains=title_query)  # Case-insensitive search for title
    if location_query:
        jobs = jobs.filter(location__icontains=location_query)  # Case-insensitive search for location
    if job_type_query:
        jobs = jobs.filter(job_type=job_type_query)  # Exact match for job type

    # Pass the filtered jobs and query data to the template
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'title_query': title_query,
        'location_query': location_query,
        'job_type_query': job_type_query,
    })

@login_required
def job_detail(request, job_id):
    """Displays the details of a specific job. Requires login."""
    job = get_object_or_404(Job, id=job_id)  # Fetch the job by ID
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def save_job(request, job_id):
    """Allows a logged-in user to save a job."""
    job = get_object_or_404(Job, id=job_id)
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    return JsonResponse({
        'saved': created,
        'message': "Job saved successfully" if created else "Job was already saved"
    })

@login_required
def create_alert(request):
    """Handles creation of job alerts for logged-in users."""
    if request.method == "POST":
        keyword = request.POST.get("keyword", "").strip()
        location = request.POST.get("location", "").strip()

        if not keyword or not location:
            return JsonResponse({'created': False, 'error': 'Keyword and location are required.'})

        alert, created = JobAlert.objects.get_or_create(
            user=request.user, keyword=keyword, location=location
        )
        return JsonResponse({'created': created})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def job_alerts(request):
    alerts = JobAlert.objects.filter(user=request.user)
    return render(request, 'jobs/job_alerts.html', {'alerts': alerts})

from django.shortcuts import render

def user_dashboard(request):
    # Add context if necessary
    return render(request, 'jobs/user_dashboard.html')  # Make sure this template path is correct
