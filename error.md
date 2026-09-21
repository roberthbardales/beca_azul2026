(venv) D:\Proyectos GIT\beca_azul2026>python manage.py makemigrations 
Migrations for 'control':
  applications\control\migrations\0001_initial.py
    - Create model Certificado
    - Create model Empresa
    - Create model Incidencia
    - Create model Trabajador
  applications\control\migrations\0002_initial.py
    - Add field registrado_por to incidencia
    - Add field trabajador to incidencia
    - Add field aprobado_por to certificado
    - Add field trabajador to certificado
    - Create constraint unique_trabajador_activo_empresa_dni on model trabajador
    - Create constraint certificado_fecha_vencimiento_no_antes_de_emision on model certificado
Migrations for 'users':
  applications\users\migrations\0001_initial.py
    - Create model User

(venv) D:\Proyectos GIT\beca_azul2026>python manage.py migrate       
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, control, sessions, users
Running migrations:
  Applying control.0002_initial...Traceback (most recent call last):
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\utils.py", line 87, in _execute
    return self.cursor.execute(sql)
           ^^^^^^^^^^^^^^^^^^^^^^^^
psycopg2.errors.DuplicateColumn: ya existe la columna «registrado_por_id» en la relación «control_incidencia»


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "D:\Proyectos GIT\beca_azul2026\manage.py", line 19, in <module>
    main()
  File "D:\Proyectos GIT\beca_azul2026\manage.py", line 16, in main
    execute_from_command_line(sys.argv)
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\core\management\__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\core\management\__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\core\management\base.py", line 412, in run_from_argv
    self.execute(*args, **cmd_options)
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\core\management\base.py", line 458, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\core\management\base.py", line 106, in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\core\management\commands\migrate.py", line 356, in handle
    post_migrate_state = executor.migrate(
                         ^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\migrations\executor.py", line 135, in migrate
    state = self._migrate_all_forwards(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\migrations\executor.py", line 167, in _migrate_all_forwards
    state = self.apply_migration(
            ^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\migrations\executor.py", line 252, in apply_migration
    state = migration.apply(state, schema_editor)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\migrations\migration.py", line 132, in apply
    operation.database_forwards(
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\migrations\operations\fields.py", line 108, in database_forwards
    schema_editor.add_field(
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\base\schema.py", line 713, in add_field
    self.execute(sql, params)
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\postgresql\schema.py", line 48, in execute
    return super().execute(sql, None)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\base\schema.py", line 201, in execute
    cursor.execute(sql, params)
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\utils.py", line 102, in execute
    return super().execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\utils.py", line 67, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\utils.py", line 80, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\utils.py", line 84, in _execute
    with self.db.wrap_database_errors:
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "D:\Proyectos GIT\beca_azul2026\venv\Lib\site-packages\django\db\backends\utils.py", line 87, in _execute
    return self.cursor.execute(sql)
           ^^^^^^^^^^^^^^^^^^^^^^^^
django.db.utils.ProgrammingError: ya existe la columna «registrado_por_id» en la relación «control_incidencia»


(venv) D:\Proyectos GIT\beca_azul2026>