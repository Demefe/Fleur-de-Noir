from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Categoria, Contato, Produto, Compra
from app.forms import FormCategoria, FormContato, ProdutoForm, FormCriarUsuario
from firebase_config import db
import requests


def index(request):
    avaliacoes = []
    try:
        docs = db.collection("avaliacao").limit(3).stream()
        for doc in docs:
            dados = doc.to_dict()
            dados["id"] = doc.id
            dados["nota"] = int(dados.get("nota", 0))
            avaliacoes.append(dados)
    except Exception as e:
        print(f"Erro Firebase: {e}")
        avaliacoes = []

    produtos_destaque = Produto.objects.filter(quantidade__gt=0).order_by("?")[:4]

    return render(
        request,
        "index.html",
        {
            "avaliacoes": avaliacoes,
            "produtos_destaque": produtos_destaque,
        },
    )


def quemSomos(request):
    return render(request, "quem-somos.html")


def criarUsuario(request):
    form = FormCriarUsuario(request.POST or None)
    if request.POST:
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.email = form.cleaned_data["email"]
            usuario.save()
            grupo_cliente, _ = Group.objects.get_or_create(name="Cliente")
            usuario.groups.add(grupo_cliente)
            messages.success(request, "Usuário criado com sucesso!")
            return redirect("index")
    return render(request, "add-usuario.html", {"form": form})


def faleConosco(request):
    formulario = FormContato(request.POST or None)
    if request.POST:
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Mensagem enviada!")
            return redirect("index")
    return render(request, "fale-conosco.html", {"form": formulario})


def produto_vitrine(request):
    produtos = Produto.objects.select_related("categoria").all()
    return render(request, "produto-vitrine.html", {"produtos": produtos, "produtos_api": []})

@login_required(login_url="/login/")
def comprar(request, id_prod):
    produto = get_object_or_404(Produto, id=id_prod)
    if produto.quantidade < 1:
        messages.error(request, "Produto fora de estoque.")
        return redirect("produtovitrine")
    Compra.objects.create(
        usuario=request.user, produto=produto, quantidade=1, total=produto.preco
    )
    produto.quantidade -= 1
    produto.save()
    messages.success(request, f'"{produto.nome}" adquirido com sucesso!')
    return redirect("perfil")


@login_required(login_url="/login/")
def perfil(request):
    compras = (
        Compra.objects.filter(usuario=request.user)
        .select_related("produto")
        .order_by("-data")
    )
    return render(request, "perfil.html", {"compras": compras})


@login_required(login_url="/login/")
def avaliacao(request):
    tem_compra = Compra.objects.filter(usuario=request.user).exists()
    if not tem_compra:
        messages.error(request, "Você precisa realizar uma compra para avaliar.")
        return redirect("produtovitrine")
    if request.method == "POST":
        cliente = request.POST.get("cliente")
        comentario = request.POST.get("comentario")
        nota = request.POST.get("nota")
        db.collection("avaliacao").add({
            "cliente": cliente,
            "usuario_id": request.user.id,
            "comentario": comentario,
            "nota": int(nota),
        })
        messages.success(request, "Avaliação enviada com sucesso!")
        return redirect("avaliacao")
    avaliacoes = []
    docs = db.collection("avaliacao").stream()
    for doc in docs:
        dados = doc.to_dict()
        dados["id"] = doc.id
        dados["nota"] = int(dados.get("nota", 0))
        avaliacoes.append(dados)
    return render(request, "avaliacao.html", {"avaliacoes": avaliacoes, "tem_compra": tem_compra})


@login_required(login_url="/login/")
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso restrito a administradores.")
        return redirect("index")
    return render(request, "dashboard.html")


@login_required(login_url="/login/")
def listarUsuario(request):
    if not request.user.is_staff:
        return redirect("index")
    usuarios = User.objects.all()
    return render(request, "usuario.html", {"usuarios": usuarios})


@login_required(login_url="/login/")
def editUsuario(request, id_user):
    if not request.user.is_staff:
        return redirect("index")
    usuario = get_object_or_404(User, id=id_user)
    if request.method == "POST":
        usuario.first_name = request.POST.get("first_name")
        usuario.email = request.POST.get("email")
        usuario.save()
        return redirect("usuario")
    return render(request, "edit-usuario.html", {"usuario": usuario})


@login_required(login_url="/login/")
def delUsuario(request, id_user):
    if not request.user.is_staff:
        return redirect("index")
    usuario = get_object_or_404(User, id=id_user)
    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuário removido!")
        return redirect("usuario")
    return render(request, "del-usuario.html", {"usuario": usuario})


@login_required(login_url="/login/")
def listarCategoria(request):
    if not request.user.is_staff:
        return redirect("index")
    categorias = Categoria.objects.all()
    return render(request, "categoria.html", {"categorias": categorias})


@login_required(login_url="/login/")
def addCategoria(request):
    if not request.user.is_staff:
        return redirect("index")
    formulario = FormCategoria(request.POST or None)
    if request.POST:
        if formulario.is_valid():
            formulario.save()
            return redirect("categoria")
    return render(request, "add-categoria.html", {"form": formulario})


@login_required(login_url="/login/")
def editCategoria(request, id_cat):
    if not request.user.is_staff:
        return redirect("index")
    categoria = get_object_or_404(Categoria, id=id_cat)
    formulario = FormCategoria(request.POST or None, instance=categoria)
    if request.POST:
        if formulario.is_valid():
            formulario.save()
            return redirect("categoria")
    return render(request, "edit-categoria.html", {"form": formulario})


@login_required(login_url="/login/")
def delCategoria(request, id_cat):
    if not request.user.is_staff:
        return redirect("index")
    categoria = get_object_or_404(Categoria, id=id_cat)
    if request.method == "POST":
        categoria.delete()
        return redirect("categoria")
    return render(request, "del-categoria.html", {"categoria": categoria})


@login_required(login_url="/login/")
def listarContato(request):
    if not request.user.is_staff:
        return redirect("index")
    contatos = Contato.objects.all()
    return render(request, "contato.html", {"contato": contatos})


@login_required(login_url="/login/")
def delContato(request, id_cont):
    if not request.user.is_staff:
        return redirect("index")
    contato = get_object_or_404(Contato, id=id_cont)
    if request.method == "POST":
        contato.delete()
        return redirect("contato")
    return render(request, "del-contato.html", {"contato": contato})


@login_required(login_url="/login/")
def listarProduto(request):
    if not request.user.is_staff:
        return redirect("index")
    produtos = Produto.objects.all()
    return render(request, "produto.html", {"produtos": produtos})


@login_required(login_url="/login/")
def addProduto(request):
    if not request.user.is_staff:
        return redirect("index")
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("produto")
    else:
        form = ProdutoForm()
    return render(request, "add-produto.html", {"form": form})


@login_required(login_url="/login/")
def editProduto(request, id_prod):
    if not request.user.is_staff:
        return redirect("index")
    produto = get_object_or_404(Produto, id=id_prod)
    if request.method == "POST":
        imagem_antiga = produto.imagem
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            if not request.FILES.get("imagem"):
                produto.imagem = imagem_antiga
            form.save()
            return redirect("produto")
    else:
        form = ProdutoForm(instance=produto)
    return render(request, "edit-produto.html", {"form": form, "produto": produto})


@login_required(login_url="/login/")
def delProduto(request, id_prod):
    if not request.user.is_staff:
        return redirect("index")
    produto = get_object_or_404(Produto, id=id_prod)
    if request.method == "POST":
        produto.delete()
        return redirect("produto")
    return render(request, "del-produto.html", {"produto": produto})


@login_required(login_url="/login/")
def vendas(request):
    if not request.user.is_staff:
        return redirect("index")
    compras = Compra.objects.select_related("produto", "usuario").order_by("-data")
    return render(request, "vendas.html", {"compras": compras})


@login_required(login_url="/login/")
def delCompra(request, id_compra):
    if not request.user.is_staff:
        return redirect("index")
    compra = get_object_or_404(Compra, id=id_compra)
    if request.method == "POST":
        compra.delete()
        messages.success(request, "Compra removida.")
        return redirect("vendas")
    return render(request, "del-compra.html", {"compra": compra})


@login_required(login_url="/login/")
def avaliacao_admin(request):
    if not request.user.is_staff:
        return redirect("index")
    avaliacoes = []
    docs = db.collection("avaliacao").stream()
    for doc in docs:
        dados = doc.to_dict()
        dados["id"] = doc.id
        dados["nota"] = int(dados.get("nota", 0))
        avaliacoes.append(dados)
    return render(request, "avaliacao-admin.html", {"avaliacoes": avaliacoes})


@login_required(login_url="/login/")
def delAvaliacao(request, id_aval):
    if not request.user.is_staff:
        return redirect("index")
    if request.method == "POST":
        db.collection("avaliacao").document(id_aval).delete()
        messages.success(request, "Avaliação removida.")
        return redirect("avaliacaoadmin")
    aval = db.collection("avaliacao").document(id_aval).get().to_dict()
    return render(request, "del-avaliacao.html", {"avaliacao": aval})


def index(request):
    avaliacoes = []
    try:
        docs = db.collection("avaliacao").limit(3).stream()
        for doc in docs:
            dados = doc.to_dict()
            dados["id"] = doc.id
            avaliacoes.append(dados)
    except:
        avaliacoes = []

    produtos_destaque = Produto.objects.filter(quantidade__gt=0).order_by("?")[:4]

    return render(
        request,
        "index.html",
        {
            "avaliacoes": avaliacoes,
            "produtos_destaque": produtos_destaque,
        },
    )
