JAZZMIN_SETTINGS = {
    "site_title": "Fenix Administration",
    "site_header": "Fenix",
    "site_brand": "Fenix",
    "site_logo": "image/Fenix.png",
    "login_logo": "#image/Fenix.png",
    "login_logo_dark": "#image/Fenix.png",
    "site_logo_classes": "img-collapsible img-logo-width-50",

    "site_icon": "image/Fenix.png",

    "welcome_sign": "Welcome to the Fenix",

    "copyright": "Asadbek Fenix Ltd",

    "search_model": ["auth.User", "auth.Group"],

    "user_avatar": "image/default.avif",

    "topmenu_links": [

        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},

        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        {"model": "auth.User"},

        {"app": "books"},
    ],

    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    "show_sidebar": True,

    "navigation_expanded": True,

    "hide_apps": [],

    "hide_models": [],

    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],

    "custom_links": {
        "books": [{
            "name": "Make Messages",
            "url": "make_messages",
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    "related_modal_active": False,

    "custom_css": "common/css/main.css",
    "custom_js": "common/js/main.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,

    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},

}

JAZZMIN_UI_TWEAKS = {
    # "theme": "cyborg",
    # "dark_mode_theme": "darkly",
}
