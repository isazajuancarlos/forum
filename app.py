from flask import Flask
from ruta import bp
from controlador import sess, login, csrf, limpiar_html

app = Flask( __name__ )
app.config.from_object( 'config' )

sess.init_app( app )
login.init_app( app )
csrf.init_app( app )

# Filtro de plantilla que sanea HTML (allowlist) en el punto de render.
app.add_template_filter( limpiar_html, 'limpio' )

app.register_blueprint( bp, url_prefix='/' )

application = app
