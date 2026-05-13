var ReportaEvaluadorEvent = {

    init: function () {
        this.loadCombos();
        this.loadTabla();        
        this.bindEvents();
    },
    loadCombos: function () {
       $("#sel_estandar").empty().append(`<option value="">Seleccione</option>`);
       $.get("/acredita/api/estandares/" + idMacroproceso, function (data) {
                    data.forEach(e => {
                        $("#sel_estandar").append(`
                            <option value="${e.id_estandar}">
                                ${e.codigo} - ${e.nombre}
                            </option>`);
                    });
                    $('#sel_estandar').select2({
                        placeholder: "Seleccione un estandar",
                        allowClear: true
                    });
        });

    },
    loadTabla: function () {
        id_macroproceso = $('#id_macroproceso').val();
        estandar_value = $('#sel_estandar').val();
        let tabla = $("#tbl_estandar_criterios").DataTable({
            destroy: true,
            ajax: {
                url: `/evaluacion/api/reportatabla?id_estandar=`+estandar_value+`&id_macroproceso=`+id_macroproceso,
                dataSrc: ""
            },
            columns: [
                { data: "estandar" },
                { data: "criterio" },
                { data: "cantidad_condiciones" },
                { data: "calificacion_criterio",
                    render: function (data, type, row) {
                        if (row.calificacion_criterio >= 0)
                            badge= '<span class="badge bg-success text-white">Sí</span>';
                        else 
                            badge = '<span class="badge bg-danger text-white">No</span>';
                        return badge;
                    }
                },
                {
                    data: null,
                    render: function (data, type, row) {
                        str_form = `<form action="evaluacion/validar" method="post">`
                            +`<input type="hidden" name="id_autoevaluacion" value="${IdAutoevaluacion}" >`
                            +`<input type="hidden" name="id_criterio" value="${row.id_criterio}" >`
                            +`<input type="hidden" name="puntaje_actual_criterio" value="${row.calificacion_criterio}" >`
                            +`<input type="hidden" name="cantidad_a_reportar" value="${row.cantidad_a_reportar}" >`
                            +`<input type="hidden" name="nombre_criterio" value="${row.criterio}" >`
                            +`<input type="hidden" name="es_precalificado" value="${row.puntaje_es_precalificado}" >`
                            +`<input type="hidden" name="regla_puntaje2_1condicion" value="${row.regla_puntaje2_condicion}" >`                            
                            +`<button type="submit" class="btn btn-sm btn-secondary me-3 btn-text-azul ">Validar</button>`
                            +`</form>`;
                        return str_form;
                    }
                }
            ],
            language: {
                url: "/static/json/es-ES.json"
            },
            paging: false,
            searching: false,
            info: false,
            ordering: true  
        });
    },
    bindEvents: function (){
        $("#sel_estandar").on("change", function () {
            ReportaEvaluadorEvent.loadTabla();
        });
    }
};
