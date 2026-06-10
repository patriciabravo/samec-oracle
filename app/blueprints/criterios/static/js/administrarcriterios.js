var CriteriosEvent = {

    init: function () {
        this.loadCombos();
        this.bindEvents();
        this.loadTabla();
        this.formvalidator();
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

    },
    bindEvents: function () {

        $('#Modal_EditarCriterio').on('hidden.bs.modal', function () {
            document.activeElement.blur();
        });
        
        $('body').on('click','.btn-edit-criterio', function () {
            let criterioId = $(this).data('id');
            let mode = $(this).data('tipo');
            $.ajax({
                url: `/acredita/criterio/${criterioId}`,
                type: 'GET',
                success: function (data) {
                    console.log(data);
                    $('#form_edit_criterio').find('#id_criterio').val(criterioId);
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
    loadTabla: function () {

        let tabla = $("#tablaCriterios").DataTable({
            destroy: true,
            ajax: {
                url: "/criterios/lista",
                dataSrc: ""
            },
            searching: true,
            dom: 'frtip',
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
                    targets: 5,
                    width: "120px",
                    className: "text-nowrap"
                }
            ],
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    },
    formvalidator: function () {
                    const form = document.getElementById("form_edit_criterio");
                    const submitButton = document.getElementById("btn_guarda_criterio");
                    const valida_datos_ipress = FormValidation.formValidation(form, {
                        fields: {
                            codigo_criterio: {
                                validators: {
                                    notEmpty: {
                                        message: "Ingrese el código IPRESS."
                                    }
                                }
                            }
                        },
                        plugins: {
                            bootstrap: new FormValidation.plugins.Bootstrap5({
                                rowSelector: ".row",
                                eleInvalidClass: "",
                                eleValidClass: ""
                            }),
                            submitButton: new FormValidation.plugins.SubmitButton()
                        }
                    })
                    .on('core.form.valid', function () {
                        let method;
                        let url;
                        const id = $('#form_edit_criterio').find('#id_criterio').val();
                        if (id) {
                            method = 'PUT';
                            url = `/criterios/${id}`;
                        } else {
                            method = 'POST';
                            url = '/criterios';
                        }
                        $.ajax({
                            url: url,
                            type: method,
                            data: $(form).serialize(),
                            success: function (res) {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Criterio Actualizado',
                                    text: 'Criterio ha sido actualizado correctamente'
                                }).then(() => {
                                    $('#Modal_EditarCriterio').modal('hide');
                                    $('#tablaCriterios').DataTable().ajax.reload();
                                });
                            },
                            error: function (err) {
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: err.responseJSON?.error || 'Ocurrió un problema al actualizar'
                                });
                            }
                        });
                    });
    }  
};