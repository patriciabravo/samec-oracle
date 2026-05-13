ACREDITACION_ACTUAL = 2026
ESTADO_ACREDITACION_ACTIVO = 1
ESTADO_ACREDITACION_INACTIVO = 1


TIPO_DOCUMENTO_DNI = 1
TIPO_DOCUMENTO_CE = 2
TIPO_DOCUMENTO_PASAPORTE = 3

TIPOS_DOCUMENTO = {
    TIPO_DOCUMENTO_DNI: "DNI",
    TIPO_DOCUMENTO_CE: "C.E.",
    TIPO_DOCUMENTO_PASAPORTE: "Pasaporte"
}

#ruta de archivos de acceso al sistema
RUTA_ARCHIVOS_AUTORIZACION = '/archivos_autorizacion'

ROLES = {
    "ROL_GERENTE_GAMCC": 1,
    "ROL_GESTOR_GAMCC": 3,
    "ROL_RED": 2,
    "ROL_EVALUADOR_IPRESS": 4,
    "ROL_COORDINADOR_IPRESS": 5,
    "ROL_ADMINISTRADOR": 6
}

ROLES_NAME= {
   1: "GERENTE_GAMCC",
   2: "GESTOR_GAMCC",
   3: "RED",
   4: "EVALUADOR",
   5: "EVALUADO",
   6:" ADMINISTRADOR"
}

MAPA_NIVEL = {
    "I-1": "nivel_i_1",
    "I-2": "nivel_i_2",
    "I-3": "nivel_i_3",
    "I-4": "nivel_i_4",
    "II-1": "nivel_ii_1",
    "II-2": "nivel_ii_2",
    "III-1": "nivel_iii_1"
}