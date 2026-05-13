var ResultadosFuenteEvent = {
    init: function () {
        this.cargarDrops();
        this.loadTabla(IdIpress);
    },
    cargarDrops: function (){
        console.log(rolPrincipal);
        /* Para Red solo Ipress de su Red */
        if (rolPrincipal===1){
            $("#filtroIpress").empty().append(`<option value="">Seleccione</option>`);
            fetch("/graficos/api/ipress_por_red/"+IdRed)
                .then(response => response.json())
                .then(data => {
                            data.forEach(e => {
                                $("#filtroIpress").append(`
                                    <option value="${e.id_ipress}">
                                        ${e.nombre_ipress}
                                    </option>`);
                            });
                            $('#filtroIpress').select2({
                                placeholder: "Seleccione una Ipress",
                                allowClear: true
                            });
            });
        }

        if (rolPrincipal===3){
            $("#filtroRed").empty().append(`<option value="">Seleccione Red</option>`);
                fetch("/graficos/api/redes")
                    .then(response => response.json())
                    .then(data => {
                                data.forEach(e => {
                                    $("#filtroRed").append(`
                                        <option value="${e.id_red}">
                                            ${e.nombre_red}
                                        </option>`);
                                });
                                $('#filtroRed').select2({
                                    placeholder: "Seleccione Red",
                                    allowClear: true
                                });
            });


            $("#filtroRed").change(function () {
                let idRed = $(this).val();
                $("#filtroIpress").html('<option value="">Cargando...</option>');
                $.ajax({
                    url: "/graficos/api/ipress_por_red/" + idRed,
                    type: "GET",
                    success: function (data) {
                        let opciones = '<option value="">Seleccione IPRESS</option>';
                        data.forEach(function (item) {
                            opciones += `<option value="${item.id_ipress}">${item.nombre_ipress}</option>`;
                        });
                        $("#filtroIpress").html(opciones);
                        $('#filtroIpress').select2({
                                placeholder: "Seleccione Ipress",
                                allowClear: true
                        });
                    }
                });

            });
        }

        if ((rolPrincipal===3) || (rolPrincipal===1)) {
            $("#filtroMacroproceso").empty().append(`<option value="">Seleccione Macroproceso</option>`);
                fetch("/graficos/api/macroprocesos")
                    .then(response => response.json())
                    .then(data => {
                                data.forEach(e => {
                                    $("#filtroMacroproceso").append(`
                                        <option value="${e.id_macroproceso}">
                                            ${e.nombre_macroproceso}
                                        </option>`);
                                });
                                $('#filtroMacroproceso').select2({
                                    placeholder: "Seleccione Macroproceso",
                                    allowClear: true
                                });
            });
        }

        
        $('#btnBuscar').on('click', function () {
            let id_ipress = $('#filtroIpress').val();
            let id_mp = $('#filtroMacroproceso').val() || 0;
            ResultadosFuenteEvent.loadTabla(id_ipress,id_mp)
        });
    },
    loadTabla: function (id_ipress, id_mp) {
        id_mp = parseInt(id_mp, 10);
        if (isNaN(id_mp)) {
            id_mp = 0;
        }

        if (rolPrincipal===2)
            id_ipress = IdIpress


        if (id_ipress){    

            var table = $('#tablaAutoevaluacion').DataTable({
                autoWidth: false,
                processing: true,
                destroy: true,
                order: [],
                ajax: {
                    url: "/resultados/api/autoevaluacion_detalle/" + id_ipress + '/id_mp/' + id_mp,
                    dataSrc: ''
                },

                rowGroup: {
                    dataSrc: ['nombre_mp', 'codigo_criterio'],
                    startRender: function (rows, group, level) {

                        // Nivel 0: Macroproceso
                        if (level === 0) {
                            return $('<tr/>')
                                .append(`<td colspan="5" >
                                            ${group}
                                        </td>`);
                        }

                        // Nivel 1: Criterio
                        if (level === 1) {
                            let r = rows.data()[0];

                            return $('<tr/>')
                                .append(`<td colspan="5" style="padding-left:20px;font-weight:bold;background:#f8f9fa">
                                            ${r.codigo_criterio} - Puntaje: ${r.puntaje_criterio}
                                        </td>`);
                        }
                    }
                },

                columns: [
                    {
                        data: "nombre_condicion",
                        width: "20%"
                    },
                    {
                        data: "nombre_tecnica",
                        width: "10%"
                    },
                    {
                        data: "nombre_proceso",
                        width: "15%"
                    },
                    {
                        data: "nombre_fuente",
                        width: "25%"
                    },
                    {
                        data: null,
                        width: "10%",
                        render: function (data, type, row) {

                            if (row.id_tecnica === 4) {

                                if (row.link_fuente) {
                                    return `<a href="${row.link_fuente}" target="_blank" class="btn btn-sm btn-primary">Ver Fuente</a>`;
                                }

                                if (row.link_reporte) {
                                    return `<a href="${row.link_reporte}" target="_blank" class="btn btn-sm btn-success">Ver Reporte</a>`;
                                }

                                if (row.ruta_archivo) {
                                    return `<a href="/uploads/${row.ruta_archivo}" target="_blank" class="btn btn-sm btn-warning">Ver Archivo</a>`;
                                }

                                return `<span class="text-muted">No reportado</span>`;
                            } else {
                                return 'Validado en visita';
                            }

                        }
                    }
                ],

                drawCallback: function () {

                    $.ajax({
                        url: `/calculoacredita/api/get_porcentaje_autoevaluacion/${id_ipress}`,
                        type: "GET",
                        dataType: "json",
                        success: function (data) {
                            $('span#muestra_porcentaje').text(data.porcentaje_obtenido + '%   ');
                        },
                        error: function () {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'No se pudo obtener el porcentaje'
                            });
                        }
                    });

                },

                pageLength: 50,

                language: {
                    emptyTable: "No existen registros para la IPRESS seleccionada"
                }

            });


        }

            $('#miBuscador').on('keyup', function () {
                var table = $('#tablaAutoevaluacion').DataTable();
                table.search(this.value).draw();
            });
    }

};
