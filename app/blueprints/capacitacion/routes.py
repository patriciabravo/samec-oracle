import os
from flask import render_template
from flask_login import login_required, current_user
from app import db
from . import capacitacion_bp
from app.models import Usuario, Persona, Rol, RolUsuario, RedEssalud, IpressEssalud


@capacitacion_bp.route("/calendario")
@login_required
def ver_calendario():
    return render_template("capacitacion/calendario.html", user=current_user, page_title="Calendario de Capacitaciones")
