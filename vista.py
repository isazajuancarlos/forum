from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, SelectField
from wtforms import TextAreaField, HiddenField, BooleanField, EmailField
from wtforms.validators import InputRequired, Email, EqualTo
import email_validator

class frm_index( FlaskForm ):
    correo = EmailField( 'correo electronico', [ InputRequired(), Email() ] )
    password = PasswordField( 'contraseña', [ InputRequired() ] )
    submit = SubmitField( 'ingresar' )

class frm_registrar( FlaskForm ):
    nombre = StringField( 'nombre', [ InputRequired() ] )
    password = PasswordField( 'contraseña', [ InputRequired() ] )
    correo = EmailField( 'correo electronico', [ InputRequired(), Email() ] )
    firma = StringField( 'firma', [ InputRequired() ] )
    icono = StringField( 'icono', [ InputRequired() ] )
    submit = SubmitField( 'guardar' )

class frm_tema( FlaskForm ):
    foro = HiddenField()
    titulo = StringField( 'titulo', [ InputRequired() ] )
    contenido = TextAreaField('contenido')
    destacado = BooleanField()
    submit = SubmitField( 'publicar' )

class frm_foro( FlaskForm ):
    nombre = StringField( 'nombre', [ InputRequired() ] )
    imagen = StringField( 'imagen', [ InputRequired() ] )
    descripcion = StringField( 'descripcion', [ InputRequired() ] )
    categoria = SelectField(u'categoria', coerce=int)
    usuario = SelectField(u'usuario', coerce=int)
    submit = SubmitField( 'crear' )

class frm_mensaje( FlaskForm ):
    mensaje = HiddenField()
    accion = HiddenField()
    contenido = TextAreaField('contenido')
    submit = SubmitField( 'publicar' )

class frm_titulo( FlaskForm ):
    tema = HiddenField()
    titulo = StringField( 'titulo', [ InputRequired() ] )
    destacado = BooleanField()
    submit = SubmitField( 'actualizar' )

class frm_perfil( FlaskForm ):
    password = PasswordField( 'nueva contraseña' )  # opcional: vacío = no cambiar
    actual = PasswordField( 'contraseña actual' )   # requerida solo para cambiar la contraseña
    firma = StringField( 'firma', [ InputRequired() ] )
    icono = StringField( 'icono', [ InputRequired() ] )
    submit = SubmitField( 'actualizar' )

class frm_categorias( FlaskForm ):
    nombre = StringField( 'nombre', [ InputRequired() ] )
    submit = SubmitField( 'crear' )

class link( FlaskForm ):
    p = HiddenField()
    m = HiddenField()
    submit = SubmitField()
