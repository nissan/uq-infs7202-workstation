
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import UserDetail, Qualification, WorkExperience
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .forms import UserDetailFullForm

from django.shortcuts import redirect

from pydantic import BaseModel, Field, ValidationError
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from django.conf import settings

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain.prompts import ChatPromptTemplate

from rest_framework import viewsets
from .serializers import QualificationSerializer, WorkExperienceSerializer

from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

class QualificationViewSet(viewsets.ModelViewSet):
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class WorkExperienceViewSet(viewsets.ModelViewSet):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset


class BioSuggestions(BaseModel):
    suggestions: List[str] = Field(description="List of improved resume bio alternatives")

@login_required
def suggest_bio(request, user_id):
    user_detail = get_object_or_404(UserDetail, id=user_id)
    bio = user_detail.bio or "Experienced professional in the tech industry."

    # Define the structured output parser using your schema
    parser = JsonOutputParser(pydantic_object=BioSuggestions)

    # Define the prompt
    prompt = PromptTemplate(
        template=(
            "You are a professional resume writer.\n"
            "Rewrite the following summary to improve its impact and clarity. "
            "Provide 5 alternative versions.\n\n"
            "{format_instructions}\n\n"
            "Bio: {bio}"
        ),
        input_variables=["bio"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Set up the chain
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.7)
    chain = prompt | llm | parser

    try:
        result = chain.invoke({"bio": bio})
        suggestions = result["suggestions"]
    except ValidationError as e:
        messages.error(request, "Validation error parsing the LLM response.")
        suggestions = []
    except Exception as e:
        messages.error(request, f"An error occurred while contacting the LLM: {e}")
        suggestions = []

    return render(request, "suggested_bio.html", {
        "suggestions": suggestions,
        "name": f"{user_detail.firstname} {user_detail.surname}",
        "user_id": user_detail.id
    })

@login_required
def select_bio(request, user_id):
    new_bio = request.GET.get("newbio")
    user_detail = get_object_or_404(UserDetail, id=user_id)
    user_detail.bio = new_bio
    user_detail.save()
    messages.success(request, "Bio updated successfully.")
    return redirect("myresume")

@login_required
def chatui(request, user_id):
    user = get_object_or_404(UserDetail, id=user_id)
    return render(request, "chatui.html", {
        "name": f"{user.firstname} {user.surname}",
        "bio": user.bio or "No bio provided"
    })

@csrf_exempt
@login_required
def chatbot(request):
    if request.method == "POST":
        try:
            history = json.loads(request.body)

            # Turn the chat history into a Langchain prompt
            prompt = ChatPromptTemplate.from_messages(history)
            llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.7)

            chain = prompt | llm
            response = chain.invoke({})

            return JsonResponse({"message": response.content})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

def index(request):
    return render(request, "landingpage.html")

@login_required
def myresume(request):
    # Get or create a UserDetail from the current user
    user_details, created = UserDetail.objects.get_or_create(
        user=request.user,
        defaults={
            "firstname": request.user.first_name or "NoFirstName",
            "surname": request.user.last_name or "NoSurname",
            "mobileno": "0400000000",  # Default mobile number
            "bio": "This user hasn't written a bio yet."  # Default bio
        }
    )

    qualifications = Qualification.objects.filter(user=user_details)
    work_experience = WorkExperience.objects.filter(user=user_details)

    context = {
        "name": f"{user_details.firstname} {user_details.surname}",
        "mobileno": user_details.mobileno,
        "qualifications": qualifications,
        "work_experience": work_experience,
        "bio": user_details.bio,
        "user_id": user_details.id
    }

    return render(request, "resume.html", context)

def about(request):
    return render(request, "about.html")

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
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

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class SubscriberCreateView(CreateView):
    model = UserDetail
    form_class = UserDetailFullForm
    template_name = "subscriber_form.html"
    success_url = reverse_lazy("manage")

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
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

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
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