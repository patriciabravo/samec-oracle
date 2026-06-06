from flask import jsonify
from app import db
from app.models import IpressEssalud,RedEssalud, Distrito, Provincia, Departamento
from flask_login import login_required

class IpressService:

    @staticmethod
    @login_required
    def get_ipress_list():
        query = (
            db.session.query(
                    IpressEssalud.id_ipress,
                    IpressEssalud.codigo_ipress,
                    IpressEssalud.nombre_ipress,
                    IpressEssalud.nivel_ipress,
                    IpressEssalud.tipo_ipress,
                    IpressEssalud.id_red,
                    IpressEssalud.es_activo,
                    RedEssalud.nombre_red,
                    Distrito.id_distrito,
                    Distrito.distrito,
                    Provincia.id_provincia,
                    Provincia.provincia,
                    Departamento.id_departamento,
                    Departamento.departamento
            )
            .outerjoin(RedEssalud,RedEssalud.id_red == IpressEssalud.id_red)
            .outerjoin(Distrito,Distrito.id_distrito == IpressEssalud.id_distrito)
            .outerjoin(Provincia,Provincia.id_provincia == Distrito.id_provincia)
            .outerjoin(Departamento,Departamento.id_departamento == Provincia.id_departamento)
        )
        return [
            {
                "id_ipress": row.id_ipress,
                "codigo_ipress": row.codigo_ipress,
                "nombre_ipress": row.nombre_ipress,
                "nivel_ipress": row.nivel_ipress,
                "tipo_ipress": row.tipo_ipress,
                "es_activo": row.es_activo,
                "id_red": row.id_red,
                "nombre_red": row.nombre_red,
                "id_distrito": row.id_distrito,
                "distrito": row.distrito,
                "id_provincia": row.id_provincia,
                "provincia": row.provincia,
                "id_departamento": row.id_departamento,
                "departamento": row.departamento,
            }
            for row in query.all()
        ]
    

    @staticmethod
    @login_required
    def obtener_ipress(ipress_id):        
        result = (
                db.session.query(
                    IpressEssalud,
                    Distrito,
                    Provincia,
                    Departamento
                )
                .outerjoin(Distrito,Distrito.id_distrito == IpressEssalud.id_distrito)
                .outerjoin(Provincia,Provincia.id_provincia == Distrito.id_provincia)
                .outerjoin(Departamento,Departamento.id_departamento == Provincia.id_departamento)
                .filter(IpressEssalud.id_ipress == ipress_id)
                .first()
            )
        if not result:
            return None
        ipress, distrito, provincia, departamento = result
        return {
            "id_ipress": ipress.id_ipress,
            "codigo_ipress": ipress.codigo_ipress,
            "nombre_ipress": ipress.nombre_ipress,
            "nivel_ipress": ipress.nivel_ipress,
            "tipo_ipress": ipress.tipo_ipress,
            "id_red": ipress.id_red,
            "id_distrito": ipress.id_distrito,
            "id_provincia": provincia.id_provincia if provincia else None,
            "id_departamento": departamento.id_departamento if departamento else None,
            "distrito": distrito.distrito if distrito else None,
            "provincia": provincia.provincia if provincia else None,
            "departamento": departamento.departamento if departamento else None,
            "activo": ipress.es_activo
        }

    @staticmethod
    @login_required
    def actualizar_ipress(ipress_id, data):
        print('data--->',data)
        ipress = IpressEssalud.query.get(ipress_id)
        if not ipress:
            return None
        ipress.codigo_ipress = data.get("codigo_ipress",ipress.codigo_ipress)
        ipress.nombre_ipress = data.get("nombre_ipress",ipress.nombre_ipress)
        ipress.tipo_ipress = data.get("sel_tipo_ipress",ipress.tipo_ipress)
        ipress.nivel_ipress = data.get("sel_nivel_ipress",ipress.nivel_ipress)
        ipress.id_red = data.get("sel_red_ipress",ipress.id_red)
        ipress.id_distrito = data.get("sel_distrito", ipress.id_distrito)
        ipress.es_activo = data.get("estado_ipress", ipress.es_activo)
        db.session.commit()
        return {
            "success": True,
            "message": "IPRESS actualizada correctamente"
        }
                
    @staticmethod
    @login_required
    def crear_ipress(data):
        print(data)
        ipress = IpressEssalud(
            codigo_ipress=data.get("codigo_ipress"),
            nombre_ipress=data.get("nombre_ipress"),
            tipo_ipress = data.get("tipo_ipress"),
            nivel_ipress = data.get("nivel_ipress"),
            id_red=data.get("id_red"),
            id_distrito=data.get("id_distrito"),
            es_activo=data.get("es_activo",1)
        )
        print('hola--',ipress)
        db.session.add(ipress)
        db.session.commit()
        return ipress

    @staticmethod
    @login_required
    def delete(ipress_id):
        ipress = IpressEssalud.query.get(ipress_id)
        if not ipress:
            return False
        db.session.delete(ipress)
        db.session.commit()
        return True
            
    @staticmethod
    @login_required
    def get_departamentos():
        departamentos = Departamento.query.order_by(
            Departamento.departamento
        ).all()
        return jsonify([
            {
                "id": d.id_departamento,
                "nombre": d.departamento
            }
            for d in departamentos
        ])
    
    @staticmethod
    @login_required
    def get_provincias(id_departamento):
        provincias = Provincia.query.filter_by(
            id_departamento=id_departamento
        ).order_by(
            Provincia.provincia
        ).all()
        return jsonify([
            {
                "id": p.id_provincia,
                "nombre": p.provincia
            }
            for p in provincias
        ])

    @staticmethod
    @login_required
    def get_distritos(id_provincia):
        distritos = Distrito.query.filter_by(
            id_provincia=id_provincia
        ).order_by(
            Distrito.distrito
        ).all()
        return jsonify([
            {
                "id": d.id_distrito,
                "nombre": d.distrito
            }
            for d in distritos
        ])