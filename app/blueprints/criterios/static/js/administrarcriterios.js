var CriteriosEvent = {

    init: function () {
        this.loadCombos();
        this.bindEvents();
        this.loadTabla();
    },
    loadCombos: function () {

        $.get("/acredita/procesosinstitucionales", function (data) {
            let sel = $("#sel_procesoinstitucional");
            sel.empty().append(`<option value="">Seleccione</option>`);
            data.forEach(m => {
                sel.append(`<option value="${m.id_proceso}">
                    ${m.nombre_proceso}
                </option>`);
            });
            $('#sel_procesoinstitucional').select2({
                placeholder: 'Seleccione ..',
                allowClear: true
            });
        });

        $('body').on('click','.btn-edit-criterio', function () {
            let criterioId = $(this).data('id');
            let mode = $(this).data('tipo');
            $.ajax({
                url: `/acredita/criterio/${criterioId}`,
                type: 'GET',
                success: function (data) {
                    console.log(data);
                    $('#form_edit_criterio').find('#codigo_criterio').val(data.codigo_criterio);
                    $('#form_edit_criterio').find('#sel_tipo_criterio').val(data.tipo_criterio);
                    $('#form_edit_criterio').find('#sel_procesoinstitucional').val(data.id_proceso).trigger('change');
                    $('#form_edit_criterio').find('#nombre_criterio').val(data.nombre_criterio);
                    $('#form_edit_criterio').find('#puntaje_0').val(data.puntaje_0_txt);
                    $('#form_edit_criterio').find('#puntaje_1').val(data.puntaje_1_txt);
                    $('#form_edit_criterio').find('#puntaje_2').val(data.puntaje_2_txt);
                    $('#form_edit_criterio').find('#sel_nivel_i_1').val(data.nivel_i_1).trigger('change');
                    $('#form_edit_criterio').find('#sel_nivel_i_2').val(data.nivel_i_2).trigger('change');
                    $('#form_edit_criterio').find('#sel_nivel_i_3').val(data.nivel_i_3).trigger('change');
                    $('#form_edit_criterio').find('#sel_nivel_i_4').val(data.nivel_i_4).trigger('change');                    
                    $('#form_edit_criterio').find('#sel_nivel_ii_1').val(data.nivel_ii_1).trigger('change');
                    $('#form_edit_criterio').find('#sel_nivel_ii_2').val(data.nivel_ii_2).trigger('change');
                    $('#form_edit_criterio').find('#sel_nivel_iii_1').val(data.nivel_iii_1).trigger('change');
                    $('#form_edit_criterio').find('#sel_aplica_essalud').val(data.aplica_essalud).trigger('change');
                },
                error: function () {
                    alert("Error al cargar los datos del Criterio");
                }
            });
            if (mode === 'ver') {
                $('#Modal_EditarCriterio').find('input, select, textarea').prop('disabled', true);
                $('#Modal_EditarCriterio').find('.modal-footer').hide();
                $('#Modal_EditarCriterio').find('.modal-title').text('Ver Red');
            } else {
                $('#Modal_EditarCriterio').find('input, select, textarea').prop('disabled', false);
                $('#Modal_EditarCriterio').find('.modal-footer').show();
                $('#Modal_EditarCriterio').find('.modal-title').text('Editar Red');
            }
        });

    },
    bindEvents: function () {

        $('#Modal_EditarCriterio').on('hidden.bs.modal', function () {
            document.activeElement.blur();
        });
    },
    loadTabla: function () {

        let tabla = $("#tablaCriterios").DataTable({
            destroy: true,
            ajax: {
                url: "/criterios/lista",
                dataSrc: ""
            },
            columns: [
                { data: "codigo_criterio" },
                { data: "nombre_criterio" },
                { data: "tipo_criterio" },
                { data: "nombre_proceso" },
                {
                    data: "aplica_essalud",
                    render: function (data, type, row) {
                        btn_aplica = 'No';
                        if (row.aplica_essalud == '1')
                            btn_aplica = 'Si';
                        return btn_aplica;
                    }                    
                },
                {
                    data: null,
                    render: function (data, type, row) {
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-criterio" 
                        data-id="${row.id_criterio}" data-bs-toggle="modal" data-bs-target="#Modal_EditarCriterio" data-tipo="edit" >
                        <i class="fas fa-edit"></i>Editar</button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-criterio"
                        data-id="${row.id_criterio}" data-bs-toggle="modal" data-bs-target="#Modal_EditarCriterio" data-tipo="ver" >
                        <i class="fas fa-eye"></i>Ver</button>`;                           
                        return  btn_edit + '&nbsp;&nbsp;' + btn_view;
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