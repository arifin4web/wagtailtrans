
from django.conf import settings
from django.conf.urls import include, url
from django.core import urlresolvers
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin import widgets
from wagtail.wagtailcore import hooks
from wagtail.wagtailtrans.urls import languages, translations
from wagtail.wagtailtrans.models import Language


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^language/', include(
            languages, app_name='wagtailtrans',
            namespace='wagtailtrans_languages')),
        url(r'^translate/', include(
            translations, app_name='wagtailtrans',
            namespace='wagtailtrans_translations')),
    ]


@hooks.register('register_settings_menu_item')
def register_language_menu_item():
    return MenuItem(
        'Languages',
        urlresolvers.reverse('wagtailtrans_languages:index'),
        classnames='icon icon-snippet',
        order=1000,
    )


@hooks.register('register_page_listing_buttons')
def page_translations_menu(page, page_perms, is_parent=False):
    if not hasattr(page, 'language'):
        return
    if hasattr(page, 'canonical_page') and page.canonical_page:
        return

    yield widgets.ButtonWithDropdownFromHook(
        'Translate into',
        hook_name='wagtailtrans_dropdown_hook',
        page=page,
        page_perms=page_perms,
        is_parent=is_parent,
        priority=10)


@hooks.register('wagtailtrans_dropdown_hook')
def page_translations_menu_items(page, page_perms, is_parent=False):
    prio = 1
    exclude_lang = None

    if hasattr(page, 'language') and page.language:
        exclude_lang = page.language

    languages = Language.objects.filter(
        live=True)
    if exclude_lang:
        languages = languages.exclude(pk=exclude_lang.pk)

    translations = page.get_translations()

    languages = languages.exclude(
        code__in=[x.language.code for x in translations]
    )
    for language in languages:
        lang = [x for x in settings.LANGUAGES if x[0] == language.code][0]
        yield widgets.Button(
            '%s' % lang[1],
            urlresolvers.reverse(
                'wagtailtrans_translations:add', kwargs={
                    'page': page.pk, 'language': language.code}),
            priority=prio)

        prio += 1
