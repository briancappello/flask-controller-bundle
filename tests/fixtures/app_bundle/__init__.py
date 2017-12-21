from flask_unchained import Bundle


class AppBundle(Bundle):
    app_bundle = True
    blueprint_names = ['one', 'two']
