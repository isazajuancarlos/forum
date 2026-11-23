from flask import session, redirect, request, url_for, render_template
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, logout_user, current_user, login_user, login_required
from markupsafe import escape
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import sys
import smtplib
import nh3
from modelo import *
from vista import *

sess = Session()
login = LoginManager()
csrf = CSRFProtect()


def es_admin():
    # Autorización por COLUMNA DE ROL (usuario.is_admin), nunca por nombre: el
    # nombre es identidad, no permiso (dos campos distintos). El admin se concede
    # poniendo is_admin = 1 en la BD. Fail-closed: si la columna no existe o es
    # falsa, nadie es admin.
    return current_user.is_authenticated and bool( getattr(current_user, 'is_admin', False) )


def limpiar_html(texto):
    # Sanea HTML provisto por el usuario con una allowlist (nh3/ammonia) antes de
    # renderizarlo, para cerrar el XSS almacenado sin perder el formato legítimo.
    if texto is None:
        return ''
    return nh3.clean(str(texto))

# clase para login manager
class Usuario( UserMixin ):
    pass

# función para cargar datos de usuario
@login.user_loader
def load_user( id ):
    try:
        c = 'select * from usuario where id = %s'
        res = get_one( c, [ id ] )
        if not res:
            return
        user = Usuario()
        user.id = res['id']
        user.fecha =  res['fecha']
        user.nombre =  res['nombre']
        user.password =  res['password']
        user.correo =  res['correo']
        user.firma =  res['firma']
        user.icono =  res['icono']
        user.is_admin = res.get('is_admin', 0)
    except:
        print( sys.exc_info() )
        user = ''
    return user

# NOTA DE SEGURIDAD: se eliminó `request_loader`. Permitía autenticarse como
# cualquier usuario enviando su `id` en el formulario (bypass de autenticación).
# La app usa login por sesión (`login_user`), que no lo necesita.

# accesos no autorizados
@login.unauthorized_handler
def unauthorized_handler():
    return redirect( url_for('bp.index') )

def rangos( id ):
    try:
        consulta = '''
        select count(mensaje.id) as contador
        from mensaje
        where usuario_id = %s
        '''
        mensaje = get_one( consulta, [ id ] )
        mensaje = mensaje['contador']
        consulta = '''
        select count(chocolate.id) as contador
        from chocolate
        inner join mensaje on chocolate.mensaje_id = mensaje.id
        where mensaje.usuario_id=%s
        '''
        choco = get_one( consulta, [ id ] )
        choco = choco['contador']
        if mensaje >= 0 and mensaje < 50:
            img = 'img/acero.png'
            rango = 'acero'
        elif mensaje >= 50 and mensaje < 100:
            img = 'img/cuarzo.png'
            rango = 'cuarzo'
        elif mensaje >= 100 and mensaje < 150:
            img = 'img/zafiro.png'
            rango = 'zafiro'
        elif mensaje >= 150 and mensaje < 250:
            img = 'img/amatista.png'
            rango = 'amatista'
        elif mensaje >= 250 and mensaje < 350:
            img = 'img/aquamarina.png'
            rango = 'aquamarina'
        elif mensaje >= 350 and mensaje < 450:
            img = 'img/esmeralda.png'
            rango = 'esmeralda'
        elif mensaje >= 450 and mensaje < 600:
            img = 'img/turquesa.png'
            rango = 'turquesa'
        elif mensaje >= 600 and mensaje < 1000:
            img = 'img/brillante.png'
            rango = 'brillante'
        elif mensaje >= 1000 and mensaje < 2000:
            img = 'img/opalo.png'
            rango = 'opalo'
        elif mensaje >= 2000 and mensaje < 3000:
            img = 'img/diamante_amarillo.png'
            rango = 'diamante amarillo'
        elif mensaje >= 3000 and mensaje < 5000:
            img = 'img/diamante_superior.png'
            rango = 'diamante superior'
        elif mensaje >= 5000 and mensaje < 7000:
            img = 'img/tiara_magica.gif'
            rango = 'tiara magica'
        elif mensaje >= 7000 and mensaje < 9000:
            img = 'img/tiara_sagrada.gif'
            rango = 'tiara sagrada'
        elif mensaje >= 9000 and mensaje < 10000:
            img = 'img/imperial_rojo.png'
            rango = 'imperial rojo'
        elif mensaje >= 10000 and mensaje < 20000:
            img = 'img/imperial_azul.png'
            rango = 'imperial azul'
        elif mensaje >= 20000 and mensaje < 40000:
            img = 'img/imperial_negro.png'
            rango = 'imperial negro'
        elif mensaje >= 40000:
            img = 'img/imperial_dorado.png'
            rango = 'imperial dorado'
        else:
            mensaje = 0
            choco = 0
            img = 'img/acero.png'
            rango = 'acero'
    except:
        print( sys.exc_info() )
        mensaje = 0
        choco = 0
        img = 'img/acero.png'
        rango = 'acero'
    return mensaje, choco, img, rango

# cerrar sesión
def cerrar_sesion():
	logout_user()
	return redirect( url_for('bp.index') )

def index():
    return redirect( url_for('bp.foros') )

def iniciar():
    form = frm_index()
    return render_template( 'index.html', form = form )

def ingresar():
    try:
        correo = request.form['correo']
        c = 'select * from usuario where correo = %s limit 1'
        res = get_one( c, [ correo ] )
        if not res:
            return redirect( url_for('bp.foros') )
        elif not check_password_hash( res['password'], request.form['password'] ):
            return redirect( url_for('bp.foros') )
        else:
            user = Usuario()
            user.id = res['id']
            user.fecha =  res['fecha']
            user.nombre =  res['nombre']
            user.password =  res['password']
            user.correo =  res['correo']
            user.firma =  res['firma']
            user.icono =  res['icono']
            user.is_admin = res.get('is_admin', 0)
            login_user( user )
    except:
        print( sys.exc_info() )
    return redirect( url_for('bp.foros') )

def registro():
    form = frm_registrar()
    form.firma.data = "https://i.imgur.com/T0UIbJz.gif"
    form.icono.data = "https://i.imgur.com/qMROBxH.png"
    return render_template( 'registrar.html', form = form )

# Nombres reservados: mientras la autorización de admin se base en el nombre
# (ver es_admin y SECURITY.md), nadie puede registrarse con uno de estos, o
# escalaría a admin con solo elegir el nombre.
NOMBRES_RESERVADOS = { 'webmaster', 'admin', 'administrador', 'root', 'moderador' }

def registrar():
    try:
        nombre = request.form['nombre']
        if nombre.strip().lower() in NOMBRES_RESERVADOS:
            return redirect( url_for('bp.registro') )
        c = '''insert into usuario
        ( fecha, nombre, password, correo, firma, icono ) values
        ( %s, %s, %s, %s, %s, %s )
        '''
        set_dat( c, [
        datetime.now(),
        nombre,
        generate_password_hash( request.form['password'] ),
        request.form['correo'],
        request.form['firma'],
        request.form['icono']
        ] )
        return redirect( url_for('bp.index') )
    except:
        print( sys.exc_info() )
        return redirect( url_for('bp.registrar') )

def foros():
    form = link()
    datos = { "categoria":[], "foro":[] }
    c = 'select id, nombre from categoria'
    categoria = get_all( c, [] )
    for cat in categoria:
        try:
            datos[ 'categoria' ].append( cat['nombre'] )
            c = '''
            select foro.id, foro.nombre, foro.descripcion, foro.imagen,
            sum( coalesce(tema.cnt, 0) ) as num_tema,
            sum( coalesce(mensaje.cnt, 0) ) as num_mensaje,
            (select tema.titulo from tema join mensaje on tema.id = mensaje.tema_id
            where tema.foro_id = foro.id order by mensaje.id desc limit 1) as titulo,
            (select mensaje.fecha from mensaje join tema on tema.id = mensaje.tema_id
            where tema.foro_id = foro.id order by mensaje.id desc limit 1) as fecha,
            (select usuario.icono from usuario join tema on usuario.id = tema.usuario_id
            join mensaje on tema.id = mensaje.tema_id where tema.foro_id = foro.id
            order by mensaje.id desc limit 1) as icono,
            (select usuario.nombre from usuario join tema on usuario.id = tema.usuario_id
            join mensaje on tema.id = mensaje.tema_id where tema.foro_id = foro.id
            order by mensaje.id desc limit 1) as usuario
            from foro left join (select tema.id, tema.foro_id, count(tema.id) as cnt
            from tema group by tema.id, tema.foro_id) tema on foro.id = tema.foro_id
            left join(select mensaje.tema_id, count(mensaje.id) as cnt
            from mensaje group by mensaje.tema_id) mensaje on tema.id = mensaje.tema_id
            join categoria on categoria.id = foro.categoria_id
            where categoria.id = %s
            group by foro.id, foro.nombre, foro.descripcion, foro.imagen
            '''
            res = get_all( c, [ cat['id'] ] )
            datos['foro'].append( res )
        except:
            print( sys.exc_info() )
            return redirect( url_for('bp.cerrar_sesion') )
    if current_user.is_authenticated:
        estado = rangos( current_user.id )
    else:
        estado = ''
    return render_template(
    'foros.html',
    form = form,
    datos = datos,
    estado = estado
    )

@login_required
def crear_foro():
    if not es_admin():
        return redirect( url_for('bp.cerrar_sesion') )
    form = frm_foro()
    c = 'select id, nombre from categoria'
    aux = get_all( c, [] )
    form.categoria.choices = [ (c['id'], c['nombre']) for c in aux ]
    c = 'select id, nombre from usuario'
    aux = get_all( c, [] )
    form.usuario.choices = [ (c['id'], c['nombre']) for c in aux ]
    c = 'select nombre from foro'
    foro = get_all( c, [] )
    return render_template( 'foro.html', form = form, foro = foro )

@login_required
def guardar_foro():
    if not es_admin():
        return redirect( url_for('bp.cerrar_sesion') )
    try:
        c = '''insert into foro
        ( fecha, nombre, imagen, descripcion, categoria_id, usuario_id ) values
        ( %s, %s, %s, %s, %s, %s )
        '''
        set_dat( c, [
        datetime.now(),
        request.form['nombre'],
        request.form['imagen'],
        request.form['descripcion'],
        request.form['categoria'],
        request.form['usuario']
        ] )
    except:
        print( sys.exc_info() )
    return redirect( url_for('bp.crear_foro') )

def temas():
    try:
        if 'p' in request.form:
            id = request.form['p']
            session['foro'] = id
        else:
            id = session['foro']
        c = '''
        select foro.id, foro.nombre, foro.imagen, foro.descripcion, usuario.nombre as usuario
        from foro inner join usuario on foro.usuario_id = usuario.id
        where foro.id = %s limit 1'''
        foro = get_all( c, [ id ])
        for f in foro:
            session['id'] = f['id']
            session['nombre'] = f['nombre']
            session['imagen'] = f['imagen']
            session['descripcion'] = f['descripcion']
            session['usuario'] = f['usuario']
    except:
        print( sys.exc_info() )
    form = link()
    try:
        c = '''select tema.id, tema.fecha, tema.titulo, tema.vista, tema.destacado,usuario.nombre,
        usuario.icono, count(mensaje.id) as respuestas,
        (select mensaje.fecha from mensaje where mensaje.tema_id = tema.id order by mensaje.tema_id desc,
        mensaje.fecha desc limit 1) as ultimo_fecha,
        (select usuario.icono from usuario inner join mensaje on usuario.id = mensaje.usuario_id
        where mensaje.tema_id = tema.id order by mensaje.tema_id desc, mensaje.fecha desc limit 1) as ultimo_icono,
        (select usuario.nombre from usuario inner join mensaje on usuario.id = mensaje.usuario_id
        where mensaje.tema_id = tema.id order by mensaje.tema_id desc, mensaje.fecha desc limit 1) as ultimo_nombre
        from tema inner join usuario on usuario.id = tema.usuario_id
        inner join mensaje on tema.id = mensaje.tema_id where tema.foro_id = %s and tema.destacado = True
        group by tema.id, tema.titulo, tema.vista, usuario.nombre, usuario.icono order by tema.fecha desc;
        '''
        dest = get_all( c, [ session['id'] ] )
    except:
        print( sys.exc_info() )
        return redirect( url_for('bp.foros') )
    try:
        c = '''select tema.id, tema.fecha, tema.titulo, tema.vista, tema.destacado,usuario.nombre,
        usuario.icono, count(mensaje.id) as respuestas,
        (select mensaje.fecha from mensaje where mensaje.tema_id = tema.id order by mensaje.tema_id desc,
        mensaje.fecha desc limit 1) as ultimo_fecha,
        (select usuario.icono from usuario inner join mensaje on usuario.id = mensaje.usuario_id
        where mensaje.tema_id = tema.id order by mensaje.tema_id desc, mensaje.fecha desc limit 1) as ultimo_icono,
        (select usuario.nombre from usuario inner join mensaje on usuario.id = mensaje.usuario_id
        where mensaje.tema_id = tema.id order by mensaje.tema_id desc, mensaje.fecha desc limit 1) as ultimo_nombre
        from tema inner join usuario on usuario.id = tema.usuario_id
        inner join mensaje on tema.id = mensaje.tema_id where tema.foro_id = %s and tema.destacado = False
        group by tema.id, tema.titulo, tema.vista, usuario.nombre, usuario.icono order by tema.fecha desc;
        '''
        gral = get_all( c, [ session['id'] ] )
    except:
        print( sys.exc_info() )
        return redirect( url_for('bp.foros') )
    if current_user.is_authenticated:
        estado = rangos( current_user.id )
    else:
        estado = ''
    return render_template(
    'temas.html',
    destacado = dest,
    general = gral,
    estado = estado,
    form = form )

@login_required
def crear_tema():
    form = frm_tema()
    form.foro.data = session['foro']
    return render_template( 'tema.html', form = form )

@login_required
def guardar_tema():
    try:
        if request.form.getlist('destacado'):
            sw = True
        else:
            sw = False
        c = '''insert into tema
        ( fecha, titulo, vista, destacado, foro_id, usuario_id ) values
        ( %s, %s, %s, %s, %s, %s )
        '''
        set_dat( c, [
        datetime.now(),
        request.form['titulo'],
        0,
        sw,
        session['id'],
        current_user.id
        ] )
        c = 'select id from tema order by id desc limit 1'
        reg = get_one( c, [] )
        c = '''insert into mensaje
        ( fecha, contenido, tema_id, usuario_id ) values
        ( %s, %s, %s, %s )
        '''
        set_dat( c, [
        datetime.now(),
        limpiar_html( request.form['contenido'] ),
        reg['id'],
        current_user.id
        ])
    except:
        print( sys.exc_info() )
    return redirect( url_for('bp.temas') )

@login_required
def titulo():
    id = request.form['p']
    c = 'select titulo,destacado from tema where id = %s'
    tem = get_one( c, [ id ] )
    form = frm_titulo()
    form.tema.data = id
    form.titulo.data = tem['titulo']
    form.destacado.data = tem['destacado']
    return render_template( 'titulo.html', form = form )

@login_required
def actualizar_titulo():
    titulo = request.form['titulo']
    tema_id = request.form['tema']
    if es_admin():
        # El admin puede editar cualquier tema y marcarlo como destacado.
        sw = True if request.form.getlist('destacado') else False
        c = 'update tema set titulo = %s, destacado = %s where id = %s'
        set_dat( c, [ titulo, sw, tema_id ] )
    else:
        # El autor solo puede editar el título de SU tema; no puede destacarlo.
        c = 'update tema set titulo = %s where id = %s and usuario_id = %s'
        set_dat( c, [ titulo, tema_id, current_user.id ] )
    return redirect( url_for('bp.temas') )

def mensajes():
    if 'p' in request.form:
        session['tema'] = request.form['p']
    form = link()
    try:
        m = {
            'usuario_id':[],
            'usuario_fecha':[],
            'usuario_icono':[],
            'usuario_nombre':[],
            'usuario_firma':[],
            'mensaje_id':[],
            'mensaje_fecha':[],
            'mensaje_contenido':[],
            'tema_id':[],
            'tema_titulo':[],
            'cita':[],
            'chocolate':[],
            'chocolates':[],
            'mensajes':[],
            'choco':[],
            'img':[],
            'rango':[]
        }
        consulta = 'update tema set vista = vista + 1 where id = %s'
        set_dat( consulta, [ session['tema'] ] )
        consulta = '''
        select usuario.id as usuario_id, usuario.fecha as usuario_fecha, usuario.icono as usuario_icono,
        usuario.nombre as usuario_nombre, usuario.firma as usuario_firma, mensaje.id as mensaje_id,
        mensaje.fecha as mensaje_fecha, mensaje.contenido as mensaje_contenido, tema.id as tema_id,
        tema.titulo as tema_titulo
        from usuario inner join mensaje on usuario.id = mensaje.usuario_id
        inner join tema on tema.id = mensaje.tema_id
        where tema.id = %s order by mensaje.fecha asc
        '''
        res_mensajes = get_all( consulta, [ session['tema'] ] )
        for t in res_mensajes:
            c = { 'icono':[], 'usuario':[], 'contenido':[] }
            consulta = 'select * from cita where mensaje_id = %s '
            cita = get_all( consulta, [ t['mensaje_id'] ] )
            for x in cita:
                c['icono'].append( x['icono'] )
                c['usuario'].append( x['usuario'] )
                c['contenido'].append( x['contenido'] )
            consulta = 'select count(id) as contador from chocolate where mensaje_id = %s and usuario_id = %s'
            if current_user.is_authenticated:
                chocolate = get_one( consulta, [ t['mensaje_id'], current_user.id ] )
            else:
                chocolate = 0
            consulta = 'select count(id) as contador from chocolate where mensaje_id = %s'
            chocolates = get_one( consulta, [ t['mensaje_id'] ] )
            consulta = 'select count(id) as contador from mensaje where usuario_id = %s'
            mensajes = get_one( consulta, [ t['usuario_id'] ] )
            if chocolate:
                chocolate = chocolate['contador']
            else:
                chocolate = 0
            if chocolates:
                chocolates = chocolates['contador']
            else:
                chocolates = 0
            if mensajes:
                mensajes = mensajes['contador']
            else:
                mensajes = 0
            estado = rangos( t['usuario_id'] )
            choco = estado[1]
            img = estado[2]
            rango = estado[3]
            m['usuario_id'].append( t['usuario_id'] )
            m['usuario_fecha'].append( t['usuario_fecha'] )
            m['usuario_icono'].append( t['usuario_icono'] )
            m['usuario_nombre'].append( t['usuario_nombre'] )
            m['usuario_firma'].append( t['usuario_firma'] )
            m['mensaje_id'].append( t['mensaje_id'] )
            m['mensaje_fecha'].append( t['mensaje_fecha'] )
            m['mensaje_contenido'].append( t['mensaje_contenido'] )
            m['tema_id'].append( t['tema_id'] )
            m['tema_titulo'].append( t['tema_titulo'] )
            m['cita'].append(c)
            m['chocolate'].append( chocolate )
            m['chocolates'].append( chocolates )
            m['mensajes'].append( mensajes )
            m['choco'].append( choco )
            m['img'].append( img )
            m['rango'].append( rango )
        if current_user.is_authenticated:
            estado = rangos( current_user.id )
        else:
            estado = ''
    except:
        print( sys.exc_info() )
        return redirect( url_for('bp.temas') )
    return render_template(
    'mensajes.html',
    mensajes = m,
    estado = estado,
    form = form )

@login_required
def mensaje():
    act = request.form.get('p')
    m = request.form.get('m')
    aux = ''
    form = frm_mensaje()
    form.accion.data = act
    if act == 'editar':
        form.mensaje.data = m
        c = 'select contenido from mensaje where id = %s'
        c = get_one( c, [ m ] )
        form.contenido.data = c['contenido']
    elif act == 'citar':
        form.accion.data = act
        form.mensaje.data = m
        aux = { "icono":[],"usuario":[],"contenido":[] }
        consulta = 'select icono,usuario,contenido from cita where mensaje_id = %s'
        cita = get_all( consulta, [ m ] )
        for c in cita:
            aux['icono'].append( c['icono'] )
            aux['usuario'].append( c['usuario'] )
            aux['contenido'].append( c['contenido'] )
        consulta = '''
        select mensaje.contenido,usuario.nombre,usuario.icono
        from mensaje inner join usuario on usuario.id = mensaje.usuario_id
        where mensaje.id = %s
        '''
        cita = get_one( consulta, [ m ] )
        if cita:
            aux['contenido'].append( cita['contenido'] )
            aux['usuario'].append( cita['nombre'] )
            aux['icono'].append( cita['icono'] )
    return render_template( 'mensaje.html', cita = aux, form = form )

@login_required
def accion_mensaje():
    try:
        tema = session['tema']
        c = 'update tema set fecha = %s where id = %s'
        set_dat( c, [ datetime.now(), tema ] )
    except:
        print( sys.exc_info() )
    if request.form['accion'] == 'editar':
        try:
            contenido = limpiar_html( request.form['contenido'] )
            mensaje = request.form['mensaje']
            if es_admin():
                c = 'update mensaje set contenido = %s where id = %s'
                set_dat( c, [ contenido, mensaje ] )
            else:
                # Solo el autor puede editar su propio mensaje.
                c = 'update mensaje set contenido = %s where id = %s and usuario_id = %s'
                set_dat( c, [ contenido, mensaje, current_user.id ] )
        except:
            print( sys.exc_info() )
    elif request.form['accion'] == 'citar':
        try:
            contenido = limpiar_html( request.form['contenido'] )
            mensaje = request.form['mensaje']
            tema = session['tema']
            usuario = current_user.id
            fecha = datetime.now()
            c = 'insert into mensaje(contenido,tema_id,usuario_id,fecha)values(%s,%s,%s,%s)'
            set_dat( c, [ contenido, tema, usuario, fecha ] )
            c = 'select id from mensaje order by id desc limit 1'
            tem = get_one( c, [] )
            c = '''select usuario.icono, usuario.nombre, mensaje.contenido from mensaje
            inner join usuario on usuario.id = mensaje.usuario_id
            where mensaje.id = %s'''
            aux = get_one( c, [ mensaje ] )
            icono = aux['icono']
            usuario = aux['nombre']
            contenido = aux['contenido']
            mensaje = tem['id']
            c = 'insert into cita(icono,usuario,contenido,mensaje_id)values(%s,%s,%s,%s)'
            set_dat( c, [ icono,usuario,contenido,mensaje ] )
            try:
                c = '''
                    select tema.titulo, usuario.correo from tema inner join usuario
                    on tema.usuario_id = usuario.id where tema.id = %s
                    '''
                aux = get_one( c, [ session['tema'] ] )
                asunto = f"nuevo mensaje en el tema {aux['titulo']}"
                consulta = '''
                select correo
                from usuario
                where id = %s
                '''
                correo = get_one( consulta, [ aux['correo'] ] )
                mensaje = f'''
                {escape(current_user.nombre)} publicó:
                <br>
                {escape(contenido)}
                '''
                send_mail( asunto,correo,mensaje )
            except:
                print( sys.exc_info() )
        except:
            print( sys.exc_info() )
    elif request.form['accion'] == 'responder':
        try:
            contenido = limpiar_html( request.form['contenido'] )
            tema = session['tema']
            usuario = current_user.id
            fecha = datetime.now()
            consulta = '''
            insert into mensaje
            (contenido,tema_id,usuario_id,fecha)
            values
            (%s,%s,%s,%s)
            '''
            set_dat( consulta, [ contenido, tema, usuario, fecha ] )
            try:
                c = '''
                    select tema.titulo, usuario.correo from tema inner join usuario
                    on tema.usuario_id = usuario.id where tema.id = %s
                    '''
                aux = get_one( c, [ session['tema'] ] )
                asunto = f"nuevo mensaje en el tema {aux['titulo']}"
                correo = aux['correo']
                mensaje = f'''
                {escape(current_user.nombre)} publicó:
                <br>
                {escape(contenido)}
                '''
                send_mail( asunto,correo,mensaje )
            except:
                print( sys.exc_info() )
        except:
            print( sys.exc_info() )
    return redirect( url_for('bp.mensajes') )

@login_required
def mistemas():
    form = link()
    ts = {
        "id":[],
        "fecha":[],
        "titulo":[],
        "vista":[],
        "nombre":[],
        "icono":[],
        "respuestas":[],
        "ultimo_fecha":[],
        "ultimo_icono":[],
        "ultimo_nombre":[]
    }
    consulta = '''
    select foro.imagen,foro.descripcion,usuario.nombre
    from foro inner join usuario on foro.usuario_id=usuario.id
    where foro.id=%s
    '''
    foro = get_one( consulta, [ session['foro'] ] )
    session['foro_des'] = foro['descripcion']
    session['moderador'] = foro['nombre']
    session['foro_imagen'] = foro['imagen']
    consulta = '''
    select tema.id,tema.fecha,tema.titulo,tema.vista,usuario.nombre,usuario.icono,count(mensaje.id) as respuestas
    from tema
    inner join usuario on usuario.id=tema.usuario_id
    inner join mensaje on tema.id=mensaje.tema_id
    where tema.foro_id=%s and usuario.id = %s
    group by tema.id,tema.titulo,tema.vista,usuario.nombre,usuario.icono
    order by tema.fecha desc
    '''
    t1 = get_all( consulta, [ session['foro'], current_user.id ] )
    for i in t1:
        ts['id'].append(i['id'])
        ts['fecha'].append(i['fecha'])
        ts['titulo'].append(i['titulo'])
        ts['vista'].append(i['vista'])
        ts['nombre'].append(i['nombre'])
        ts['icono'].append(i['icono'])
        ts['respuestas'].append(i['respuestas'])
        consulta = '''
        select mensaje.fecha,usuario.icono,usuario.nombre
        from mensaje inner join usuario on mensaje.usuario_id=usuario.id
        where mensaje.tema_id = %s
        order by mensaje.tema_id desc,mensaje.fecha desc;
        '''
        us = get_one( consulta, [ i['id'] ] )
        ts['ultimo_fecha'].append(us['fecha'])
        ts['ultimo_icono'].append(us['icono'] )
        ts['ultimo_nombre'].append(us['nombre'])
    return render_template( 'mistemas.html', temas=ts, estado=rangos(current_user.id),  form=form )

@login_required
def perfil():
    form = frm_perfil()
    form.firma.data = current_user.firma
    form.icono.data = current_user.icono
    if current_user.is_authenticated:
        estado = rangos( current_user.id )
    else:
        estado = ''
    return render_template( 'perfil.html', form = form, estado = estado )

@login_required
def guardar_perfil():
    firma = request.form['firma']
    icono = request.form['icono']
    password = request.form.get('password', '')
    if password:
        # Solo se recifra la contraseña si se escribió una nueva.
        c = 'update usuario set password = %s, firma = %s, icono = %s where id = %s'
        set_dat( c, [ generate_password_hash( password ), firma, icono, current_user.id ] )
    else:
        c = 'update usuario set firma = %s, icono = %s where id = %s'
        set_dat( c, [ firma, icono, current_user.id ] )
    return redirect( url_for('bp.perfil') )

@login_required
def privado():
    pass

def send_mail(asunto,correo,mensaje):
    # Credenciales SMTP por variable de entorno — nunca hardcodeadas. Ver .env.example.
    remitente = os.environ.get("FORUM_SMTP_USER", "")
    clave = os.environ.get("FORUM_SMTP_PASSWORD", "")
    host = os.environ.get("FORUM_SMTP_HOST", "smtp.gmail.com")
    puerto = int(os.environ.get("FORUM_SMTP_PORT", "587"))
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = correo
    msg['Subject'] = asunto
    msg.attach( MIMEText(mensaje, 'html') )
    try:
        s = smtplib.SMTP(host, puerto)
        s.starttls()
        s.login(remitente, clave)
        s.sendmail( msg['From'], msg['To'], msg.as_string() )
    except:
        print( sys.exc_info() )

@login_required
def categorias():
    if not es_admin():
        return redirect( url_for('bp.cerrar_sesion') )
    form = frm_categorias()
    try:
        c = 'select nombre from categoria'
        categoria = get_all( c, [] )
    except:
        print( sys.exc_info() )
    return render_template( 'categorias.html', categoria = categoria, form = form )

@login_required
def guardar_categoria():
    if not es_admin():
        return redirect( url_for('bp.cerrar_sesion') )
    nombre = request.form.get('nombre')
    try:
        c = 'insert into categoria(nombre)values(%s)'
        set_dat( c, [ nombre ] )
    except:
        print( sys.exc_info() )
    return redirect( url_for('bp.categorias') )

@login_required
def get_choco():
    mensaje = request.args.get('mensaje')
    div = request.args.get('div')
    c = 'insert into chocolate(usuario_id, mensaje_id)values(%s, %s)'
    set_dat( c, [ current_user.id, mensaje ] )
    c = 'select count(id) as contador from chocolate where mensaje_id = %s'
    choco = get_one( c, [ mensaje ] )
    if not choco:
        choco = 0
    else:
        choco = choco['contador']
    choco = { "cont":choco, "div":div }
    return choco
