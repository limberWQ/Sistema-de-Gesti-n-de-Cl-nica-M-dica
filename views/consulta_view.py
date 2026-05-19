from flask import render_template


def render_listar(consultas):
    #Lista completa de consultas (solo admin)
    return render_template('consulta/listar.html', consultas=consultas)


def render_registrar(medicos, pacientes):
    #Formulario para registrar una nueva consulta (solo admin)
    return render_template('consulta/registrar.html',
                           medicos=medicos, pacientes=pacientes)


def render_editar(consulta, medicos, pacientes):
    #Formulario para editar una consulta existente (solo admin)
    return render_template('consulta/editar.html',
                           consulta=consulta,
                           medicos=medicos,
                           pacientes=pacientes)
