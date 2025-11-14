from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Topic, Message, Profile
from .forms import CreateUserForm, MessageForm, UserUpdateForm, RoomForm, ProfileUpdateForm
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse

# ---------------------- Главная ----------------------
@login_required(login_url='loginPage')
def home(request):
    # получаем GET‑параметр «q» (запрос поиска)
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    # получаем GET‑параметр «filter_by»
    filter_by = request.GET.get('filter_by')  # может быть None

    # базовый QuerySet — все комнаты с предзагрузкой темы и хоста для оптимизации
    rooms = Room.objects.select_related('topic', 'host').all()

    # если есть параметр поиска «q», применяем фильтрацию по нескольким полям
    if q:
        rooms = rooms.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(topic__name__icontains=q) |
            Q(host__username__icontains=q)
        )

    # дополнительная фильтрация по активности, если указан параметр
    if filter_by == 'recent':
        # сортировка по дате обновления/создания — последние первым
        rooms = rooms.order_by('-updated')
    elif filter_by == 'topic':
        # пример: только комнаты с темой, оставляем только те, у которых тема не null
        rooms = rooms.filter(topic__isnull=False).order_by('topic__name')
   

    # темы — для отображения на странице, как фильтр‑список
    topics = Topic.objects.all()

    # контекст шаблона
    context = {
        'rooms': rooms,
        'topics': topics,
        'q': q,
        'filter_by': filter_by,
    }
    return render(request, 'base/home.html', context)
# ---------------------- Регистрация ----------------------
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт создан для {user.username}')
            return redirect('loginPage')
    context = {'form': form}
    return render(request, 'base/register.html', context)

# ---------------------- Вход ----------------------
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            Profile.objects.get_or_create(user=user)
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'base/login.html')

# ---------------------- Выход ----------------------
def logoutUser(request):
    logout(request)
    return redirect('home')

# ---------------------- Профиль ----------------------
def userProfile(request, pk):
    user = get_object_or_404(User, id=pk)
    rooms = user.participants.all()
    user_messages = Message.objects.filter(user=user).order_by('-created')
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'user_messages': user_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)

# ---------------------- Обновление профиля ----------------------
@login_required(login_url='loginPage')
def updateProfile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('user-profile', pk=request.user.id)

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'base/update_user.html', context)

# ---------------------- Комнаты ----------------------
@login_required(login_url='loginPage')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('room_detail', pk=room.id)
    return render(request, 'base/room_form.html', {'form': form})

@login_required(login_url='loginPage')
def updateRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    if room.host and request.user != room.host and not request.user.is_superuser:
        return HttpResponse('Вы не авторизованы для редактирования этой комнаты.')
    form = RoomForm(instance=room)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_detail', pk=room.id)
    return render(request, 'base/room_form.html', {'form': form})

@login_required(login_url='loginPage')
def deleteRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    if room.host and request.user != room.host and not request.user.is_superuser:
        return HttpResponse('Вы не авторизованы для удаления этой комнаты.')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='loginPage')
def room_detail(request, pk):
    room = get_object_or_404(Room, id=pk)
    messages_list = room.message_set.all().order_by('created')
    if request.user.is_authenticated:
        room.participants.add(request.user)
    context = {
        'room': room,
        'messages': messages_list,
    }
    return render(request, 'base/room.html', context)

# ---------------------- Сообщения ----------------------
@login_required(login_url='loginPage')
def deleteMessage(request, pk):
    message = get_object_or_404(Message, id=pk)
    if request.user != message.user:
        return HttpResponse('Вы не авторизованы для удаления этого сообщения.')
    if request.method == 'POST':
        message.delete()
        return redirect('room_detail', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message})

# ---------------------- Лента активности ----------------------
@login_required(login_url='loginPage')
def activityPage(request):
    messages_list = Message.objects.all().order_by('-created')
    unread_messages = Message.objects.exclude(read_by=request.user)
    unread_count_by_room = {}
    for msg in unread_messages:
        room_id = msg.room.id
        unread_count_by_room[room_id] = unread_count_by_room.get(room_id, 0) + 1
    context = {
        'messages': messages_list,
        'unread_count_by_room': unread_count_by_room,
    }
    return render(request, 'base/activity.html', context)

# ---------------------- О нас ----------------------
def about(request):
    return render(request, 'base/about.html')
