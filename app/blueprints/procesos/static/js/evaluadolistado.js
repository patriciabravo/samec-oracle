var ProcessEvent = {

    tabla: null,

    init: function () {
        this.loadTablaProcesos();
    },

    // ===============================================================
    // DATATABLE PRINCIPAL
    // ===============================================================
    loadTablaProcesos: function () {

        this.tabla = $("#tablaProcesosInstitucionales").DataTable({
            destroy: true,
            ajax: {
                url: "/procesos/api/process",
                dataSrc: "procesos" 
            },
            columns: [
                { data: "nombre_proceso"
                },
                {
                data: "estado",
                render: function(data, type, row) {
                                if (data === "pendiente") {
                                    return '<span class="badge bg-danger text-white">Pendiente</span>';
                                }

                                if (data === "en proceso") {
                                    return '<span class="badge bg-warning text-white">En Proceso</span>';
                                }

                                if (data === "completado") {
                                    return '<span class="badge bg-success text-white">Completado</span>';
                                }
                }
                },
                { data: "cantidad_observaciones"
                },
                {
                    data: "id_proceso",
                    render: (id, type, row) => `
                        <form action="/procesos/evaluado/${id}/fuentes" method="POST">
                            <input type="hidden" name="id_autoevaluacion" value="${IdAutoevaluacion}">
                            <input type="hidden" name="id_proceso_institucional" value="${id}">
                            <button type="submit" class="btn btn-sm btn-secondary me-3 btn-text-azul"><i class="bi bi-file-earmark-text me-1"></i>Registrar evidencias</button>
                        </form>`
                }
            ],
            language: { url: "/static/json/es-ES.json" }
        });

    }
};
