var CalculoAcreditaEvent = {
    init: function () {
        this.loadTabla();
        this.bindEvents();
    },
    loadTabla: function () {
    $.ajax({
        url: `/calculoacredita/calculo/id_autoevaluacion/`+ID_AUTOEVALUACION+'/id_ipress/'+ID_IPRESS,
        type: "GET",
        success: function(res) {
            var tieneDatos = (res.tiene_datos === true) || (res.data && res.data.length > 0 && (res.data[0].L_sumatoria_total_pmt || 0) > 0);
            $('#btnExportarExcel').prop('disabled', !tieneDatos);
            if (tieneDatos) {
                $('#btnExportarExcel').attr('title', 'Exportar resultados a Excel');
            } else {
                $('#btnExportarExcel').attr('title', 'No hay datos para exportar');
            }

            $('#tablaAcredita').DataTable({
                data: res.data,
                columns: [
                    { data: "macroproceso" },
                    { data: "E_valor_estructura" },
                    { data: "F_valor_proceso" },
                    { data: "G_valor_resultado" },
                    { data: "H_cantidad_criterios_reportados" },
                    
                    { data: "I_puntaje_maximo_estructura" },
                    { data: "J_puntaje_maximo_proceso" },
                    { data: "K_puntaje_maximo_resultado" },
                    { data: "L_sumatoria_total_pmt" },

                    { data: "Q_puntaje_maximo_estructura_peso" },
                    { data: "R_puntaje_maximo_proceso_peso" }, 
                    { data: "S_puntaje_maximo_resultado_peso" },
                    { data: "T_sumatoria_total" },

                    { data: "U_ptc_estructura_criterio" },
                    { data: "V_ptc_proceso_criterio" }, 
                    { data: "W_ptc_resultado_criterio" },

                    { data: "Z_puntaje_obtenido_por_tipo_macroproceso_estructura" },
                    { data: "AA_puntaje_obtenido_por_tipo_macroproceso_proceso" }, 
                    { data: "AB_puntaje_obtenido_por_tipo_macroproceso_resultado" },

                    { data: "AD_ptje_max_proporcion_estructura" },
                    { data: "AE_ptje_max_proporcion_proceso" }, 
                    { data: "AF_ptje_max_proporcion_resultado" },

                    { data: "AH_ptje_obtenido_mp_estructura" },
                    { data: "AI_ptje_obtenido_mp_proceso" }, 
                    { data: "AJ_ptje_obtenido_mp_resultado" },
                    { data: "AK_sumatoria_puntaje_obtenido_mp_todos" },

                    { data: "AL_porcentaje_macroproceso_constante" },
                    
                    { data: "AM_puntaje_min_por_macroproceso" },  
                    { data: "AN_puntaje_obtenido_por_macroproceso" }, 
                    { data: "AO_cumplimiento_macroproceso" }  

                ],
                columnDefs: [
                    { 
                        targets: 4,
                        className: 'bg-secondary'
                    },
                    { 
                        targets: 8,
                        className: 'bg-secondary'
                    },
                    { 
                        targets: 12,
                        className: 'bg-secondary'
                    },
                ],
                responsive: true,
                language: {
                    url: "/static/json/es-ES.json"
                },
                paging: false,
                searching: true,
                info: false,
                order: [] 
            });

            // Pintar segunda tabla manualmente (o DataTable)
            $('#tablaCategorias').DataTable({
                data: res.categorias,
                columns: [
                    { data: "categoria" },
                    { data: "AP_puntaje_max_categoria" },
                    { data: "AQ_porcentaje_categoria" },
                    { data: "AR_total_ptje_categoria_max" },
                    { data: "AS_puntaje_max_categoria" },
                    { data: "AT_puntaje_obtenido" }
                ],
                paging: false,
                searching: true,
                info: false,
                order: [],
                footerCallback: function () {
                    $('#porcentaje').html(
                        '<strong>Porcentaje:</strong><span id="porcentaje_obtenido">' + res.porcentaje + '</span>'
                    );
                }
            });

        },
        error: function() {
            $('#btnExportarExcel').prop('disabled', true);
            $('#btnExportarExcel').attr('title', 'Error al cargar datos');
        }
    });


    $('#btnGuardarAutoevaluacion').on('click', function () {

        $.ajax({
            url: "calculoacredita/api/autoevaluacion/guardar_puntaje",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                id_ipress: ID_IPRESS,
                id_autoevaluacion: ID_AUTOEVALUACION,
                puntaje: $('span#porcentaje_obtenido').text()
            }),

            success: function (response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Resultados guardados',
                    text: 'El puntaje fue registrado correctamente',
                    confirmButtonText: 'OK'
                });
            },
            error: function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo guardar el resultado',
                    confirmButtonText: 'Cerrar'
                });

            }
        });

    });



    },
    bindEvents: function () {
        var self = this;
        $(document).on('click', '#btnExportarExcel', function () {
            if ($(this).prop('disabled')) return;
            var url = '/calculoacredita/exportar_excel/id_autoevaluacion/' + ID_AUTOEVALUACION + '/id_ipress/' + ID_IPRESS;
            window.location.href = url;
        });
    }
};
