import os
from flask import Flask, send_from_directory, current_app, redirect, url_for
from flasgger import Swagger
from flask_login import current_user
from .helpers import inline_svg 
from .extensions import db, migrate, login_manager, mail #viene de extensions
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.blueprints.auth import auth_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.usuario import usuario_bp
from app.blueprints.capacitacion import capacitacion_bp
from app.blueprints.permisos import permisos_bp
from app.blueprints.acredita import acredita_bp
from app.blueprints.procesos import procesos_bp
from app.blueprints.evaluacion import evaluacion_bp
from app.blueprints.calculoacredita import calculoacredita_bp
from app.blueprints.graficos import graficos_bp 
from app.blueprints.resultados import resultados_bp 
from app.blueprints.autoevaluacion import autoevaluacion_bp
from app.blueprints.acreditacion import acreditacion_bp
from app.blueprints.redes import redes_bp
from app.blueprints.macrorregion import macrorregion_bp
from app.blueprints.ipress import ipress_bp

from app.models.usuario import Usuario
from app.models.menu import Menu
from app.models.opcion import Opcion
from app.models.rol_opcion import RolOpcion
from app.models.ipress import IpressEssalud
from app.models.red import RedEssalud
from collections import defaultdict
from app.constants import ROLES_NAME
from app.models import Persona, Usuario, RedEssalud, IpressEssalud

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config['SQLALCHEMY_ECHO'] = True   
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(app.root_path, '..', 'uploads'))
    app.config.from_object(DevelopmentConfig)
    swagger = Swagger(app)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    elif env == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    app.jinja_env.globals['inline_svg'] = inline_svg
    app.jinja_env.globals['ROLES'] = ROLES_NAME
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(capacitacion_bp)
    app.register_blueprint(permisos_bp)
    app.register_blueprint(acredita_bp)
    app.register_blueprint(procesos_bp)
    app.register_blueprint(evaluacion_bp)
    app.register_blueprint(calculoacredita_bp)
    app.register_blueprint(graficos_bp)
    app.register_blueprint(resultados_bp)
    app.register_blueprint(autoevaluacion_bp)
    app.register_blueprint(acreditacion_bp)
    app.register_blueprint(redes_bp)
    app.register_blueprint(macrorregion_bp)
    app.register_blueprint(ipress_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.logueo"))

    @app.context_processor
    def inject_menu():        
        if not current_user.is_authenticated:
            return dict(menu_dict={})  # si no está logueado, no hay menú        
        id_rol = current_user.roles_asociados[0].id_rol    
        filas = (
            db.session.query(
                Menu.nombre_menu,
                Menu.icono_menu,
                Opcion.nombre_opcion,
                Opcion.ruta_opcion
            )
            .select_from(RolOpcion)
            .join(Opcion, RolOpcion.id_opcion == Opcion.id_opcion)
            .join(Menu, Opcion.id_menu == Menu.id_menu)
            .filter(RolOpcion.id_rol == id_rol, Opcion.activo == True)
        )
        filas = filas.all()
        menu_dict = defaultdict(list)
        for nombre_menu, icono_menu, nombre_opcion, ruta_opcion in filas:        
            resultado = nombre_menu + "#" + icono_menu
            menu_dict[resultado].append(
                {"opcion": nombre_opcion, "ruta": ruta_opcion}
            )
        return dict(menu_dict=menu_dict)    

    @app.context_processor
    def inject_role_title():
        if not current_user.is_authenticated:
            return dict(rol_titulo="")        
        # Obtiene el id_rol del usuario
        id_rol = current_user.roles_asociados[0].id_rol
        # Usa ROLES_NAME que ya está importado
        from app.constants import ROLES_NAME        
        # Obtiene el nombre del rol, si no existe usa “USUARIO”
        rol_titulo = ROLES_NAME.get(id_rol, "USUARIO")
        return dict(rol_titulo=rol_titulo)
        
    @login_manager.user_loader
    def load_user(id_usuario):
        user = Usuario.query.get(int(id_usuario))
        if user:
            ipress = IpressEssalud.query.get(user.id_ipress)
            red = RedEssalud.query.get(user.id_red)                        
            if red:
                user.red_nombre = red.nombre_red
            if ipress:
                user.ipress_nombre = ipress.nombre_ipress
                user.ipress_nivel = ipress.nivel_ipress
                red = RedEssalud.query.get(ipress.id_red)
                user.red_nombre = red.nombre_red
        return user
    
    return app
