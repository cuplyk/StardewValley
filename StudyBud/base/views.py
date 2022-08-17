from atexit import register
from pydoc_data.topics import topics
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from zmq import Message
from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower() # Get the username and password 
        password = request.POST.get('password')

        try:                                                # Check if the user exist
            user = User.objects.get(username=username)      # if not print error
        except:     
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password) # Make sure that the credential are correct

        if user is not None:    # log user in
            login(request, user)    # create a session in the data base
            return redirect('home') # redirect the user
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)

    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST': # Pass the user data
        form = UserCreationForm(request.POST)   # Go to creation form
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ''

    rooms = Room.objects.filter(        # Search bar by topic, name and description from models Room
        Q(topic__name__icontains=q) |   
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        )

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(           
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user) # add the user to the room
        return redirect('room', pk=room.id)
        

    context = {'room': room, 'room_messages': room_messages, 'participants': participants   }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()

    context ={'user': user, 'rooms': rooms, 'room_message': room_message, 'topics': topics} 
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login')     # decorater if user is  not authenticated redirect them to login page 
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)  # render a template

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)  # get the room from the database
    form = RoomForm(instance=room)  # create a form instance and pass the room object to the form

    if request.user != room.host:   # if the host is not the user room creator  return http
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)    #  process the form data
        if form.is_valid():
            form.save()
            return redirect('home')     # redirect to the home page


    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': message})

