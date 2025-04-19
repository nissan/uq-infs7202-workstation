# views_fbv.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import UserDetail
from .forms import UserDetailFullForm

def index(request):
    return render(request, "landingpage.html")

def myresume(request):
    user_details = get_object_or_404(UserDetail, id=1) # Note a hardcoded user id
    qualifications = Qualification.objects.filter(user=user_details)
    work_experience = WorkExperience.objects.filter(user=user_details)


def about(request):
    return render(request, "about.html")


def manage_subscribers(request):
    search_query = request.GET.get("search", "")
    queryset = UserDetail.objects.select_related("user")

    if search_query:
        queryset = queryset.filter(
            Q(user__username__icontains=search_query) |
            Q(firstname__icontains=search_query) |
            Q(surname__icontains=search_query)
        )

    paginator = Paginator(queryset, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "manage_subscribers.html", {
        "users": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    })

def add_subscriber(request):
    if request.method == "POST":
        form = UserDetailFullForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscriber added successfully.")
            return redirect("manage")
    else:
        form = UserDetailFullForm()
    return render(request, "subscriber_form.html", {"form": form})

def edit_subscriber(request, pk):
    user_detail = get_object_or_404(UserDetail, pk=pk)
    user = user_detail.user

    if request.method == "POST":
        form = UserDetailFullForm(request.POST, instance=user_detail)
        if form.is_valid():
            # Manually update user fields
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()

            form.save(commit=False).user = user
            user_detail.firstname = form.cleaned_data['firstname']
            user_detail.surname = form.cleaned_data['surname']
            user_detail.mobileno = form.cleaned_data['mobileno']
            user_detail.save()

            messages.success(request, "Subscriber updated successfully.")
            return redirect("manage")
    else:
        initial = {
            "username": user.username,
            "email": user.email,
            "firstname": user_detail.firstname,
            "surname": user_detail.surname,
            "mobileno": user_detail.mobileno,
        }
        form = UserDetailFullForm(initial=initial, instance=user_detail)

    return render(request, "subscriber_form.html", {"form": form, "object": user_detail})

def delete_subscriber(request, pk):
    user_detail = get_object_or_404(UserDetail, pk=pk)
    username = user_detail.user.username

    if request.method == "POST":
        user_detail.user.delete()
        messages.success(request, f"User '{username}' was deleted.")
        return redirect("manage")

    return render(request, "subscriber_confirm_delete.html", {"object": user_detail})