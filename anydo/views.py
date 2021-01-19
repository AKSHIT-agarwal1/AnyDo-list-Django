from django.shortcuts import render,redirect, get_object_or_404 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import AnydoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request,'anydo/home.html')

def signupuser(request):
    if request.method=='GET':
        return render(request,'anydo/signupuser.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1'] ==request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('current')
            except  IntegrityError:
                return render(request,'anydo/signupuser.html',{'form':UserCreationForm(), 'error':'The Username has already been taken. Please choose a different username'})
        else:
            return render(request,'anydo/signupuser.html',{'form':UserCreationForm(), 'error':'The passwords did not match'})
        
    

def loginuser(request):
    if request.method=='GET':
        return render(request,'anydo/loginuser.html',{'form': AuthenticationForm()})
    else:
        user= authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request,'anydo/loginuser.html',{'form': AuthenticationForm(), 'error':'Username and Password did not match'})
        else:
            login(request,user)
            return redirect('current')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    else:
        return redirect('home')

@login_required
def createtodo(request):
    if request.method=='GET':
        return render(request,'anydo/createtodo.html',{'form':AnydoForm()})
    else:
        try:
            form = AnydoForm(request.POST)
            newanydo = form.save(commit=False)
            newanydo.user = request.user
            newanydo.save()
            return redirect('current')
        except ValueError:
            return render(request, 'anydo/createtodo.html',{'form':AnydoForm(), 'error':'Bad Data passed in. Try again'})

@login_required
def current(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request,'anydo/currenttodos.html', {'todos' : todos })

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method=='GET':
        form = AnydoForm(instance = todo)
        return render(request,'anydo/viewstodo.html', {'todo' : todo, 'form':form })
    else:
        try:
            form = AnydoForm(request.POST, instance=todo)
            form.save()
            return redirect('current')
        except ValueError:
            return render(request, 'anydo/viewstodo.html',{ 'todo': todo,'form':form, 'error':'Bad Data passed in. Try again'})

@login_required
def completetodo(request, todo_pk): 
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('current')

@login_required
def deletetodo(request, todo_pk): 
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('current')

@login_required
def completed(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'anydo/completedtodos.html', {'todos' : todos })

        