import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Discussion, Message
from .forms import DiscussionForm

# Configure API key
genai.configure(api_key="AIzaSyAu4yTRmEMLMOJwNMTpX09oKB1zMY1gwMc")

# Home page
def home(request):
    return render(request, 'chat/home.html')

# Authenticated user page with discussions and messages
@login_required
def welcome_authenticated(request):
    discussions = request.user.discussions.all()  # Récupère les discussions liées à l'utilisateur
    selected_discussion = None
    messages_list = None

    # Vérifie si une discussion est sélectionnée
    discussion_id = request.GET.get('discussion_id')
    if discussion_id:
        selected_discussion = get_object_or_404(Discussion, id=discussion_id, user=request.user)
        messages_list = selected_discussion.messages.all()

    if request.method == 'POST':
        # Création d'une nouvelle discussion
        if 'title' in request.POST:
            form = DiscussionForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                discussion = Discussion.objects.create(title=title, user=request.user)
                return redirect(f'{request.path}?discussion_id={discussion.id}')

        # Envoi d'un message dans la discussion sélectionnée
        if 'message' in request.POST and selected_discussion:
            user_message = request.POST.get('message', '').strip()
            if user_message:
                try:
                    ai_response = get_ai_response(user_message)
                    # Envoi des messages dans la base de données
                    Message.objects.create(discussion=selected_discussion, sender='user', content=user_message)
                    Message.objects.create(discussion=selected_discussion, sender='AI', content=ai_response)
                except Exception as e:
                    messages.error(request, f"Erreur lors de la communication avec l'IA : {str(e)}")
                return redirect(f'{request.path}?discussion_id={selected_discussion.id}')
    else:
        form = DiscussionForm()

    return render(request, 'chat/welcome_authenticated.html', {
        'discussions': discussions,
        'selected_discussion': selected_discussion,
        'messages': messages_list,
        'form': form,
    })

def get_ai_response(user_message):
    try:
        # Log the input message
        print(f"User message: {user_message}")

        # Configure API key and initialize the model
        genai.configure(api_key="AIzaSyAu4yTRmEMLMOJwNMTpX09oKB1zMY1gwMc")
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate the response
        response = model.generate_content(user_message)

        # Log the raw response
        print(f"Raw response from API: {response}")

        # Extract and return the AI's response text
        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            print("Aucune réponse valide de l'IA.")
            return "Je n'ai pas pu obtenir une réponse valide de l'IA."
    
    except Exception as e:
        # Log the exception details
        print(f"Error during API communication: {str(e)}")
        return f"Désolé, une erreur s'est produite lors de la communication avec l'IA. Erreur: {str(e)}"



def welcome_non_authenticated(request):
    messages_list = []
    ai_response = None
    user_message = None

    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            # Enregistrer le message de l'utilisateur dans messages_list
            messages_list.append({'sender': 'user', 'content': user_message})
            
            # Obtenir la réponse de l'IA
            ai_response = get_ai_response(user_message)
            
            # Enregistrer la réponse de l'IA
            if ai_response:
                messages_list.append({'sender': 'AI', 'content': ai_response})

    return render(request, 'chat/welcome_non_authenticated.html', {
        'messages': messages_list,  # Liste de tous les messages
        'ai_response': ai_response,
        'message': user_message,
    })

# Vue pour supprimer une discussion
@login_required
def delete_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id, user=request.user)
    
    # Supprimer la discussion et ses messages associés
    discussion.delete()
    
    # Rediriger vers la page des discussions après la suppression
    messages.success(request, 'Discussion supprimée avec succès.')
    return redirect('welcome_authenticated')

# User registration page
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username} !')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

# Login page
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('welcome_authenticated')
        else:
            messages.error(request, 'Nom d’utilisateur ou mot de passe invalide.')
    return render(request, 'chat/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('home')
