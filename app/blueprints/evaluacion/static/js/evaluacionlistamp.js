var EvaluadorListaMpEvent = {

    init: function () {
        this.loadTabla();
    },
    loadTabla: function () {

        $.ajax({
            url: "/evaluacion/api/calculoavancecalificacionipress/" + IdIpress,
            type: "GET",
            success: function(res) {
                let porcentaje = res.porcentaje_avance_calificacion;
                let total = res.total_criterios;
                let calificados = res.total_calificados;
                // actualizar barra
                $("#resultado_avance_calificacion")
                    .css("width", porcentaje + "%")
                    .text(porcentaje + "%");

                // detalle
                $("#detalle_avance").html(
                    calificados + " de " + total + " criterios calificados"
                );

                // cambiar color según avance
                let barra = $("#resultado_avance_calificacion");

                barra.removeClass("bg-danger bg-warning bg-success");

                if (porcentaje < 40) {
                    barra.addClass("bg-danger");
                } else if (porcentaje < 80) {
                    barra.addClass("bg-warning");
                } else {
                    barra.addClass("bg-success");
                }

            }
        });


        $.ajax({
            url: "/evaluacion/api/calculoavancereportefuentes/" + IdIpress,
            type: "GET",
            success: function(res) {

                let porcentaje = res.porcentaje;
                let total = res.total_fuentes_requeridas;
                let reportadas = res.total_fuentes_reportadas;

                $("#resultado_avance_fuentes")
                    .css("width", porcentaje + "%")
                    .text(porcentaje + "%");

                $("#detalle_avance_fuentes").html(
                    reportadas + " de " + total + " fuentes reportadas"
                );

            }
        });


        $.ajax({
            url: "/evaluacion/api/calculoavance/"+IdIpress,
            type: "GET",
            success: function(res) {
                $('#tbl_evaluacion_macroprocesos').DataTable({
                    data: res,
                    columns: [
                    {
                        data: null,
                        render: function (data, type, row) {
                                return row.codigo_macroproceso+' - '+row.nombre_macroproceso;
                        }
                    },
                    { data: "avance" },
                    {
                        data: null,
                        render: function (data, type, row) {
                            if (row.id_autoevaluacion > 0){
                                str_form = `<form action="evaluacion/reportaevaluador" method="post">`
                                    +`<input type="hidden" name="id_autoevaluacion" value="${row.id_autoevaluacion}" >`
                                    +`<input type="hidden" name="id_macroproceso" value="${row.id_macroproceso}" >`
                                    +`<input type="hidden" name="nombre_macroproceso" value="${row.codigo_macroproceso} - ${row.nombre_macroproceso}" >`
                                    +`<button type="submit" class="btn btn-sm btn-secondary me-3 btn-text-azul ">Validar</button>`
                                    +`</form>`;
                                return str_form;
                            } else{
                                return 'No cuenta con autoevaluación'
                            }
                        }
                    }
                    ],
                    paging: false,
                    searching: true,
                    info: false,
                    order: []
                });

            }
        
        });

        $('#estadoSwitch').on('change', function () {

            console.log('entro aqui');
            let $switch = $(this);
            let id = $switch.data('id');
            let idipress = $switch.data('ipress');
            // 1 = Activado | 2 = Desactivado
            let nuevoEstado = $switch.is(':checked') ? 1 : 2;
            let estadoAnterior = nuevoEstado === 1 ? 2 : 1;
            let accionTexto = nuevoEstado === 1 ? "activar" : "desactivar";
            Swal.fire({
                    title: '¿Estás seguro?',
                    text: "Se procederá a " + accionTexto + " el reporte del evaluado",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, ' + accionTexto,
                    cancelButtonText: 'Cancelar'
                }).then(function (result) {

                    if (result.isConfirmed) {
                        $switch.prop('disabled', true);
                        $.ajax({
                            url: '/evaluacion/actualizar-estado',
                            type: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                id: id,
                                idipress: idipress,
                                estado: nuevoEstado
                            }),
                            success: function (response) {
                                if (!response.success) {
                                    Swal.fire('Error', 'No se pudo actualizar', 'error');
                                    $switch.prop('checked', estadoAnterior === 1);
                                }
                            },
                            error: function () {
                                Swal.fire('Error', 'Error del servidor', 'error');
                                $switch.prop('checked', estadoAnterior === 1);
                            },
                            complete: function () {
                                $switch.prop('disabled', false);
                            }
                        });
                    } else {
                        // Si cancela → revertir estado
                        $switch.prop('checked', estadoAnterior === 1);
                    }
                });

        });


        













    }
 
};
