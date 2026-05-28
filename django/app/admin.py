from django.contrib import admin
from app.models import Categoria, Produto

# Register your models here.
admin.site.register(Categoria)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "quantidade", "categoria", "imagem")
    search_fields = ("nome", "categoria__nome")
    list_filter = ("categoria", "preco")