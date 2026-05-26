var GraficosEvent = {
    autoevaluaciones: [],       
    init: function () {
        this.cargarDrops();
        this.cargarGrafico();
    },
    cargarDrops: function () {
        /* Para la red cargar las ipress relacionadas a la red */
        if (RolId==1){
            if ($.fn.select2 && $('#filtroIpress').hasClass("select2-hidden-accessible")) {
                $('#filtroIpress').select2('destroy');
            }
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

        /* ROL GAMCC = 2 desplegables Red e Ipress relacionados */
        if (RolId==3){
            if ($.fn.select2 && $('#filtroRed').hasClass("select2-hidden-accessible")) {
                $('#filtroRed').select2('destroy');
            }
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
                if ($.fn.select2 && $('#filtroIpress').hasClass("select2-hidden-accessible")) {
                    $('#filtroIpress').select2('destroy');
                }
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


        //Caso Rol 2
        if (RolId === 2) {
            let url = `/graficos/api/autoevaluacion/id_ipress/`+IdIpressGrafico;
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    console.log("Respuesta:", data);
                    GraficosEvent.cargarGrafico(data);
            })
            .catch(error => console.error("Error:", error));
        }


        $('#btnBuscar').on('click', function () {

            let ipress = $('#filtroIpress').val();
            let url = `/graficos/api/autoevaluacion/id_ipress/${ipress}`;

            fetch(url)
                    .then(res => res.json())
                    .then(data => {
                        if (data.length === 0) {
                            console.log("No existe autoevaluación");
                            $("#grafico_macroproceso").html("<h3><p style='text-align:center'>No existe autoevaluación</p></h3>");
                        } else{
                            let idAutoevaluacion = data[0];
                            GraficosEvent.cargarGrafico(idAutoevaluacion);
                        }

                    })
                    .catch(error => console.error("Error:", error));
        });

    },
    cargarGrafico: function (autoevaluaciones) {

        if (autoevaluaciones) {
            let url = "/graficos/api/puntajes_macroproceso?ids=" + autoevaluaciones;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                if (typeof Highcharts === "undefined") {
                    document.getElementById("grafico_macroproceso").innerHTML =
                        '<div class="text-center text-muted pt-10">Gráfico no disponible en este entorno.</div>';
                    return;
                }
                Highcharts.chart('grafico_macroproceso',{
                        chart: {
                            type: 'column',
                            inverted: true,
                            height: 800
                        },
                        title: {
                            text: 'Distribución de Puntajes por Macroproceso',
                            style: {
                                    fontSize: '18px',
                                    fontWeight: 'bold'
                                }
                        },
                        xAxis: {
                            labels: {
                                    style: {
                                        fontSize: '14px'
                                    }
                            },
                            categories: data.macroprocesos,
                            title: {
                                text: 'Macroprocesos',
                                style: {
                                    fontSize: '16px',
                                    fontWeight: 'bold'
                                }
                            },
                        },
                        yAxis: {
                            labels: {
                                    style: {
                                        fontSize: '14px'
                                    }
                            },
                            min: 0,
                            title: {
                                text: 'Cantidad',
                                style: {
                                    fontSize: '16px',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        plotOptions: {
                            column: {
                                grouping: true,
                                dataLabels: {
                                    enabled: true,
                                    formatter: function () {

                                            let index = this.point.index;

                                            let total = 0;

                                            this.series.chart.series.forEach(s => {

                                                total += s.data[index]?.y || 0;

                                            });

                                            if (total === 0) {
                                                return '0%';
                                            }

                                            return (
                                                (this.y / total) * 100
                                            ).toFixed(1) + '%';
                                        },
                                    style: {
                                        fontSize: '13px'
                                    }
                                }
                            }
                        },
                        legend: {
                            itemStyle: {
                                fontSize: '14px',
                                fontWeight: 'bold'
                            }
                        },
                        series: [
                            {
                                name: 'Puntaje 0',
                                data: data.serie_0
                            },
                            {
                                name: 'Puntaje 1',
                                data: data.serie_1
                            },
                            {
                                name: 'Puntaje 2',
                                data: data.serie_2
                            }
                        ]
                    });
            });
        }
    }
};
document.addEventListener("DOMContentLoaded", function () {
    if (typeof $ !== "undefined") {
        GraficosEvent.init();
    } else {
        console.error("jQuery no está cargado.");
    }
});