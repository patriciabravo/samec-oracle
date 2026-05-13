  README# Flask - instalar SAMEC

1. git clone el repo “git url”
2. python -m venv .venv  -- debe estar instalado python  previamente
3. .venv/Scripts/activate
4. pip install -r requirements.txt
5. si hay error en psycopg entonces instalar:  pip install psycopg[binary]
6. upgrade pip:  python -m pip install --upgrade pip
7. verifica version: pip --version
8. Encender la BD postgres y su servicio (preferencia cliente: DBeaver)
9. crear la bd llamada SAMEC (verificar el puerto 5432)
10. Copiar .env.example a .env y ajustar (BD, puerto, SECRET_KEY, etc.). Opcional: FLASK_APP=run:app para usar `flask run`.
11. verifica si existe carpeta migrations.
12. flask db init —> crea la nueva carpeta si no existe sino:  pip install flask-migrate
13. flask db migrate -m "initial migration"→ ejecuta la migracion basandose en los modelos
14. flask db upgrade  → para crear las tablas
15. flask db current → que todo este sincronizado
16. flask run (o `python run.py`) → correr la aplicacion. Si no arranca, definir FLASK_APP=run:app en .env.
17. Exportar Excel (Cálculo Acreditación): colocar el archivo "modelo excel reporte.xlsx" en la carpeta recursos/ (ver recursos/README.txt).
18.  * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000/) correo, pero la ruta real es: http://127.0.0.1:5000/auth/logueo# samec
psql -U postgres -h localhost -p 5433 -d nombre_db -f data_only.sql (data_samec.sql) data de carga inicial
