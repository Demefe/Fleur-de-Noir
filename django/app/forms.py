from django import forms
from app.models import Categoria
from app.models import Contato
from app.models import Produto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class FormCriarUsuario(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class FormCategoria(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

class FormContato(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'email', 'assunto', 'mensagem']

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'imagem', 'quantidade', 'preco', 'categoria']