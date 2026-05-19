from flask import render_template


def render_listar(pacientes, usuarios_disponibles=None):
    #Lista de pacientes registrados (vista admin).
    return render_template('paciente/listar.html',
                           pacientes=pacientes,
                           usuarios_disponibles=usuarios_disponibles or [])


def render_registrar(usuarios_disponibles):
    #Formulario para asignar perfil de paciente a un usuario existente
    return render_template('paciente/registrar.html',
                           usuarios_disponibles=usuarios_disponibles)


def render_registrar_con_error(usuarios_disponibles, error: str):
    return render_template('paciente/registrar.html',
                           usuarios_disponibles=usuarios_disponibles,
                           error=error)


def render_editar(paciente):
   #Formulario de edición de perfil paciente
    return render_template('paciente/editar.html', paciente=paciente)


def render_listar_consultas(consultas):
    #Historial de consultas del paciente autenticado (o admin)
    return render_template('paciente/listar_consultas.html', consultas=consultas)


def render_cancelar_consulta(consulta):
   #Confirmación de cancelación de una consulta
    return render_template('paciente/cancelar_consulta.html', consulta=consulta)
