
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import UserDetail, Qualification, WorkExperience
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .forms import UserDetailFullForm

def index(request):
    return render(request, "landingpage.html")

def myresume(request):
    user_details = get_object_or_404(UserDetail, id=1) # Note a hardcoded user id
    qualifications = Qualification.objects.filter(user=user_details)
    work_experience = WorkExperience.objects.filter(user=user_details)

    context = {
        "name": f"{user_details.firstname} {user_details.surname}",
        "mobileno": user_details.mobileno,
        "qualifications": qualifications,
        "work_experience": work_experience,
    }
    return render(request, "resume.html", context)

def about(request):
    return render(request, "about.html")

class ManageSubscribersView(ListView):
    model = UserDetail
    template_name = "manage_subscribers.html"
    context_object_name = "users"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user")
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(firstname__icontains=search_query) |
                Q(surname__icontains=search_query)
            )
        return queryset

class SubscriberCreateView(CreateView):
    model = UserDetail
    form_class = UserDetailFullForm
    template_name = "subscriber_form.html"
    success_url = reverse_lazy("manage")

class SubscriberUpdateView(UpdateView):
    model = UserDetail
    form_class = UserDetailFullForm
    template_name = "subscriber_form.html"
    success_url = reverse_lazy("manage")

    def get_initial(self):
        initial = super().get_initial()
        user = self.object.user
        initial['username'] = user.username
        initial['email'] = user.email
        return initial

    def form_valid(self, form):
        # Update the User object manually
        user = self.object.user
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']
        if form.cleaned_data['password']:
            user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

class SubscriberDeleteView(DeleteView):
    model = UserDetail
    template_name = "subscriber_confirm_delete.html"
    success_url = reverse_lazy("manage")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        username = self.object.user.username
        self.object.user.delete()
        messages.success(request, f"User '{username}' deleted.")
        return super().delete(request, *args, **kwargs)