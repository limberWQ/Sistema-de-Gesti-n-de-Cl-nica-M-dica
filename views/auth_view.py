from flask import render_template


def render_login():
    return render_template('auth/login.html')


def render_registro():
    return render_template('auth/registro.html')
