# pcm/admin.py (arquivo novo)
from django.contrib import admin

# Remove as ações padrão em TODO o site admin
admin.site.disable_action('delete_selected')

class CleanAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_delete'] = True  # ou False se quiser esconder até o botão apagar
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

# Agora usa como base em todos os seus admins:
# class SalaAdmin(CleanAdmin):