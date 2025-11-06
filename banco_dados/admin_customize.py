from admin_interface.models import Theme

def customize_admin_theme():
    # Facebook blue: #1877F2
    theme, created = Theme.objects.get_or_create(name="Quality Governance Plan")
    theme.active = True
    theme.title = "Quality Governance Plan"
    theme.title_color = "#FFFFFF"
    theme.logo_color = "#FFFFFF"
    theme.css_header_background_color = "#1877F2"
    theme.css_header_text_color = "#FFFFFF"
    theme.css_header_link_color = "#FFFFFF"
    theme.css_header_link_hover_color = "#1456A0"
    theme.css_module_background_color = "#F4F6FA"
    theme.css_module_background_selected_color = "#1877F2"
    theme.css_module_text_color = "#1877F2"
    theme.css_module_link_color = "#1877F2"
    theme.css_module_link_selected_color = "#FFFFFF"
    theme.css_module_link_hover_color = "#1456A0"
    theme.css_save_button_background_color = "#1877F2"
    theme.css_save_button_background_hover_color = "#1456A0"
    theme.css_save_button_text_color = "#FFFFFF"
    theme.save()

# Para aplicar, execute este script no shell do Django:
# python manage.py shell
# from banco_dados.admin_customize import customize_admin_theme
# customize_admin_theme()
