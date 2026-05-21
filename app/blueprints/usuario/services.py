from app import db
from app.models.persona import Persona


def guardar_persona_service(data):

    id_persona = data.get('id_persona')
    nombres = data.get('nombres')
    apellido_paterno = data.get('apellido_paterno')
    apellido_materno = data.get('apellido_materno')
    tipo_documento = data.get('tipo_documento')
    numero_documento = data.get('numero_documento')

    try:

        if id_persona:

            persona = Persona.query.get(id_persona)

            if not persona:
                return {
                    'success': False,
                    'error': 'Persona no encontrada'
                }, 404

            persona.nombres = nombres
            persona.apellido_paterno = apellido_paterno
            persona.apellido_materno = apellido_materno
            persona.tipo_documento = tipo_documento
            persona.numero_documento = numero_documento

            mensaje = 'Persona actualizada correctamente'

        else:

            persona_existente = Persona.query.filter_by(
                numero_documento=numero_documento
            ).first()

            if persona_existente:
                return {
                    'success': False,
                    'error': 'El número de documento ya existe'
                }, 400

            persona = Persona(
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento
            )

            db.session.add(persona)

            mensaje = 'Persona registrada correctamente'

        db.session.commit()

        return {
            'success': True,
            'mensaje': mensaje
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            'success': False,
            'error': str(e)
        }, 500