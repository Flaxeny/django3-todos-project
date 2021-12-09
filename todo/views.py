from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import ToDoForm
from .models import ToDo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def homepage(request):
    return render(request, 'todo/homepage.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'That username has been taken. Please create another one'})
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords didn\'t match'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
       user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
       if user is None:
           return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and Password didn\'t match'})
       else:
           login(request, user)
           return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': ToDoForm()})
    else:
        try:
            form = ToDoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': ToDoForm(), 'error': 'Bad data passed in. Try again'})

@login_required
def currenttodos(request):
    todos = ToDo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/currentodos.html', {'todos': todos})

@login_required
def completedtodos(request):
    todos = ToDo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completedtodos.html', {'todos': todos})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user = request.user)
    if request.method == "GET":
        form = ToDoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = ToDoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad info'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')