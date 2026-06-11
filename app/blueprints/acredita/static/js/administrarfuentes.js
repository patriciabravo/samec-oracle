var FuentesEvent = {

    init: function () {
        this.loadCombos();
        this.bindEvents();
        this.loadTabla();
    },
    loadCombos: function () {
        $.get("/acredita/api/macroprocesos", function (data) {
            let sel = $("#sel_macroproceso");
            sel.empty().append(`<option value="0">Seleccione</option>`);
            data.forEach(m => {
                sel.append(`<option value="${m.id_macroproceso}">
                    ${m.codigo} - ${m.nombre}
                </option>`);
            });
        });
    },
    bindEvents: function () {
        $("#sel_macroproceso").on("change", function () {
            let id_macro = $(this).val();

            $("#sel_estandar").empty().append(`<option value="0">Seleccione</option>`);
            $("#sel_criterio").empty().append(`<option value="0">Seleccione</option>`);
            if (id_macro !== "0") {
                $.get("/acredita/api/estandares/" + id_macro, function (data) {
                    data.forEach(e => {
                        $("#sel_estandar").append(`
                            <option value="${e.id_estandar}">
                                ${e.codigo} - ${e.nombre}
                            </option>
                        `);
                    });
                });
            }
            FuentesEvent.loadTabla();
        });

        $("#sel_estandar").on("change", function () {
            let id_est = $(this).val();

            $("#sel_criterio").empty().append(`<option value="0">Seleccione</option>`);

            if (id_est !== "0") {
                $.get("/acredita/api/criterios/" + id_est, function (data) {
                    data.forEach(c => {
                        $("#sel_criterio").append(`
                            <option value="${c.id_criterio}">
                                ${c.codigo} - ${c.nombre}
                            </option>
                        `);
                    });
                });
            }

            MacroprocesoEvent.loadTabla();
        });

        $('#sel_estandar').on('select2:clear', function () {
            tabla.search('').columns().search('').draw();
        });

        $("#sel_criterio").on("change", function () {
            MacroprocesoEvent.loadTabla();
        });

        $('#Modal_AddCondicion').on('hidden.bs.modal', function () {
            document.activeElement.blur();
        });
    },
    loadTabla: function () {
        let tabla = $("#tablaCombinada").DataTable({
            destroy: true,
            ajax: {
                url: "/acredita/api/combinado",
                data: {
                    id_macroproceso: $("#sel_macroproceso").val(),
                    id_estandar: $("#sel_estandar").val(),
                    id_criterio: $("#sel_criterio").val()
                },
                dataSrc: ""
            },
            columns: [
                { data: "macro" },
                { data: "estandar" },
                { data: "criterio" },
                {
                    data: null,
                    render: function (data, type, row) {
                        str_form = `<form action="condicion/actualizar" method="post">`
                            +`<input type="hidden" name="id_criterio" value="${row.id_criterio}" >`
                            +`<input type="hidden" name="nombre_criterio" value="${row.criterio}" >`
                            +`<button type="submit" class="btn btn-sm btn-secondary me-3 btn-text-azul ">Administrar condiciones</button>`
                            +`</form>`;
                        return str_form;
                    }
                }
            ],
            columnDefs: [
                {
                    targets: 3,
                    width: "120px",
                    className: "text-nowrap"
                }
            ],
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    }
};