from flask import render_template


def render_listar(medicos, usuarios_disponibles=None):
   #Lista de médicos registrados (vista admin)
    return render_template('medico/listar.html',
                           medicos=medicos,
                           usuarios_disponibles=usuarios_disponibles or [])


def render_registrar(usuarios_disponibles):
    #Formulario para asignar perfil de medico a un usuario existente
    return render_template('medico/registrar.html',
                           usuarios_disponibles=usuarios_disponibles)


def render_registrar_con_error(usuarios_disponibles, error: str):
    return render_template('medico/registrar.html',
                           usuarios_disponibles=usuarios_disponibles,
                           error=error)


def render_editar(medico):
    #Formulario de edición de perfil medico
    return render_template('medico/editar.html', medico=medico)


def render_listar_consultas(consultas):
    #Consultas visibles para el medico autenticado (o admin)
    return render_template('medico/listar_consultas.html', consultas=consultas)


def render_registrar_consulta(medicos, pacientes):
    #Formulario para que el medico (o admin) registre una nueva consulta
    return render_template('medico/registrar_consultas.html',
                           medicos=medicos, pacientes=pacientes)
