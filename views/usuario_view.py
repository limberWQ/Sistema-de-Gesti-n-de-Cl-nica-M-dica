from flask import render_template


def render_index(usuarios):
    #Lista completa de usuarios para el administrador
    return render_template('usuarios/index.html', usuarios=usuarios)


def render_crear():
    #Formulario vacio para crear un usuario
    return render_template('usuarios/create.html')


def render_crear_con_error(error: str):
    #Formulario de creacion con mensaje de error de validacion
    return render_template('usuarios/create.html', error=error)


def render_editar(usuario):
    #Formulario de edicion de un usuario (sin perfil extra)
    return render_template('usuarios/edit.html', usuario=usuario)
