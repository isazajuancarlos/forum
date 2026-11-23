import os
from datetime import timedelta

# SECRET_KEY estable desde el entorno (necesaria para que el token CSRF y las
# sesiones sobrevivan a reinicios/múltiples procesos); si no se define, se usa
# una aleatoria (válida para desarrollo de un solo proceso).
SECRET_KEY = os.environ.get( "FORUM_SECRET_KEY" ) or os.urandom( 32 )
BASEDIR = os.path.abspath( os.path.dirname(__file__) )
DEBUG = os.environ.get( "FORUM_DEBUG", "0" ) == "1"

SESSION_TYPE = "filesystem"
SESSION_COOKIE_SECURE = True
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta( minutes = 1440 )