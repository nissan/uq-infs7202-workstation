# views.py

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

# A class-based view to manage and display a paginated list of subscribers
class ManageSubscribersView(ListView):
    model = UserDetail  # This view operates on the UserDetail model
    template_name = "manage_subscribers.html"  # Template to render the list
    context_object_name = "users"  # Context variable name for the list in the template
    paginate_by = 5  # Number of users to display per page

    # Custom queryset to enable search functionality
    def get_queryset(self):
        # Use select_related to optimize DB queries by joining related User table
        queryset = super().get_queryset().select_related("user")

        # Get the search term from the query parameters (?search=...)
        search_query = self.request.GET.get("search", "")

        # If there's a search query, filter the queryset
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |  # Match username
                Q(firstname__icontains=search_query) |       # Match first name
                Q(surname__icontains=search_query)           # Match surname
            )

        return queryset  # Return the final filtered or unfiltered queryset


# A class-based view for creating a new subscriber entry
class SubscriberCreateView(CreateView):
    model = UserDetail  # The model that will be created in this form view
    form_class = UserDetailFullForm  # Custom form that likely includes both User and UserDetail fields
    template_name = "subscriber_form.html"  # Template used to render the form

    # After successful form submission, redirect to the 'manage' view (e.g., ManageSubscribersView)
    success_url = reverse_lazy("manage")

# A class-based view  for updating an existing subscriber
class SubscriberUpdateView(UpdateView):
    model = UserDetail  # The model instance to update
    form_class = UserDetailFullForm  # The form used to edit subscriber details
    template_name = "subscriber_form.html"  # Reuses the create form template

    # After successful update, redirect to the 'manage' view (list of subscribers)
    success_url = reverse_lazy("manage")

    # Pre-populate initial data for fields from the related User model
    def get_initial(self):
        initial = super().get_initial()
        user = self.object.user  # Get the related User instance
        initial['username'] = user.username  # Populate the username field
        initial['email'] = user.email  # Populate the email field
        return initial

    # Save changes to both UserDetail and the related User object
    def form_valid(self, form):
        # Get the related User object from the current UserDetail
        user = self.object.user
        # Update fields from the submitted form
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']

        # If a new password is provided, update it securely
        if form.cleaned_data['password']:
            user.set_password(form.cleaned_data['password'])

        user.save()  # Save changes to the User model
        return super().form_valid(form)  # Continue saving UserDetail via the form

# A class-based view for deleting a subscriber (UserDetail and its associated User)
class SubscriberDeleteView(DeleteView):
    model = UserDetail  # The model to be deleted
    template_name = "subscriber_confirm_delete.html"  # Template to confirm deletion
    success_url = reverse_lazy("manage")  # Redirect to the subscriber list after deletion

    # Override the default delete method to also delete the related User object
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()  # Get the UserDetail instance to be deleted
        username = self.object.user.username  # Store username for the success message

        self.object.user.delete()  # Delete the related User object (also deletes UserDetail if cascaded)

        # Show a success message to the user
        messages.success(request, f"User '{username}' deleted.")

        # Call the original delete method to complete deletion
        return super().delete(request, *args, **kwargs)