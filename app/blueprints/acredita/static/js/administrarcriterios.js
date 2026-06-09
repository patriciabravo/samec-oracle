var CriteriosEvent = {

    init: function () {
        this.loadCombos();
        this.bindEvents();
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
    }
};