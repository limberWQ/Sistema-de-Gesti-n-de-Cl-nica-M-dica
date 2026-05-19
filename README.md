Sistema de Gestión de Clínica Médica
tablas: 
-------
-Usuario(id_usuario, nombre, username, password, rol)
-Medicos(id_medico, especialidad, telefono, correo, id_usuario FK)
-Pacientes(id_paciente, edad, direccion, telefono, id_usuario FK)
-Consultas(id_consulta, fecha, diagnostico, tratamiento,
id_medico FK, id_paciente FK)


---RELACIONES
-Un usuario puede ser un médico o un paciente (según rol)
-Un médico pertenece a un usuario (1 a 1)
-Un paciente pertenece a un usuario (1 a 1)
-Un médico puede tener muchas consultas (1 a N)
-Un paciente puede tener muchas consultas (1 a N)
-Cada consulta pertenece a un médico y a un paciente (N a 1)

Estructura del proyecto

mvc_Clinica/
│
├── run.py
├── config.py
├── database.py
├── requirements.txt
│
├── controllers/
│   ├── usuario_controller.py
│   ├── medico_controller.py
│   ├── paciente_controller.py
│   └── consulta_controller.py
│   └── auth_controller.py
│
├── models/
│   ├── medico_model.py
│   ├── paciente_model.py
│   └── consulta_model.py
│   └── usuario_model.py 
│
├── views/
│   ├── medico_view.py
│   ├── usuario_view.html
│   ├── auth_view.html
│   ├── paciente_view.py
│   └── consulta_view.py
│
├── templates/
    │  
    ├── base.html
    ├── 403.html
    ├── 402.html
    ├── dashboard.html
    │
    ├── auth/
    │   ├── login.html
    │   └── registro.html
    │
    │
    ├── usuarios/
    │   ├── index.html
    │   ├── create.html
    │   └── edit.html
    │
    ├── medico/
    │   ├── listar_consultas.html
    │   ├── listar.html
    │   ├── registrar.html
    │   ├── registrar_consultas.html
    │   └── editar.html
    │
    │
    ├── paciente/
    │   ├── listar_consultas.html
    │   ├── editar.html
    │   ├── listar.html
    │   ├── canselar_consulta.html
    │   └── cancelar_consulta.html
    │
    │
    └── consulta/
        ├── listar.html
        ├── registrar.html
        └── editar.html
