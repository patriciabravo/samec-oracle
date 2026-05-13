var BandejaPersonasEvent = {

    init: function () {
        this.loadPersonasTable();
        this.bindEvents();
        this.formvalidator();
    },
    loadPersonasTable: function () {
        $('#personasTable').DataTable({
            ajax: {
                url: '/usuario/api/personas',
                dataSrc: ''
            },
            columns: [
                { data: 'id_persona'},
                { data: 'nombres_completos'},
                {
                    data: 'tipo_documento',
                    render: function (data, type, row) {
                        return row.tipo_documento_texto;
                    }
                },
                { data: 'numero_documento' },
                { data: 'fecha_registro_formato' },
                {
                    data: null,
                    render: function (data, type, row) {
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-persona" 
                        data-id="${row.id_persona}" data-bs-toggle="modal" data-bs-target="#CrearPersona" data-tipo="edit" >
                        <i class="fas fa-edit"></i> Editar </button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-persona"
                        data-id="${row.id_persona}" data-bs-toggle="modal" data-bs-target="#CrearPersona" data-tipo="ver" >
                        <i class="fas fa-eye"></i> Ver </button>`;                           
                        return  btn_edit + btn_view;
                    }
                }               
            ],
            responsive: true,
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    },
    bindEvents: function () {
        $('body').on('click','.btn-edit-persona', function () {
            let personaId = $(this).data('id');
            let mode = $(this).data('tipo');
            if (personaId !== 0){
                $.ajax({
                    url: `/usuario/api/getpersona/${personaId}`,
                    type: 'GET',
                    success: function (data) {
                        $('#id_persona').val(data.id_persona);
                        $('#nombres').val(data.nombres);
                        $('#apellido_paterno').val(data.apellido_paterno);
                        $('#apellido_materno').val(data.apellido_materno);
                        $('#tipo_documento').val(data.tipo_documento);
                        $('#numero_documento').val(data.numero_documento);                   
                    },
                    error: function () {
                        alert("Error al cargar los datos de la persona");
                    }
                });
            } else {
                $('#CrearPersona').find('input, select, textarea').val('');
            }

            if (mode === 'ver') {
                $('#CrearPersona').find('input, select, textarea').prop('disabled', true);
                $('#CrearPersona').find('.modal-footer').hide();
                $('#CrearPersona').find('.modal-title').text('Ver Persona');
            } else {
                $('#CrearPersona').find('input, select, textarea').prop('disabled', false);
                $('#CrearPersona').find('.modal-footer').show();
                $('#CrearPersona').find('.modal-title').text('Editar Persona');
            }

        });
    },
    formvalidator: function () {

                    const form = document.getElementById("form_nueva_persona");
                    const submitButton = document.getElementById("btn_guarda_persona");
                    const valida_datos_persona = FormValidation.formValidation(form, {
                        fields: {
                            "nombres": {
                                validators: {
                                    notEmpty: {
                                        message: "Nombres son requeridos"
                                    }
                                }
                            },
                            "apellido_paterno": {
                                validators: {
                                    notEmpty: {
                                        message: "Apellido paterno es requerido"
                                    }
                                }
                            },
                            "apellido_materno": {
                                validators: {
                                    notEmpty: {
                                        message: "Apellido materno es requerido"
                                    }
                                }
                            },
                            "tipo_documento": {
                                validators: {
                                    notEmpty: {
                                        message: "Tipo de documento es requerido"
                                    }
                                }
                            }
                        },
                        plugins: {
                            trigger: new FormValidation.plugins.Trigger({
                                event: {
                                    password: !1
                                }
                            }),
                            bootstrap: new FormValidation.plugins.Bootstrap5({
                                rowSelector: ".fv-row",
                                eleInvalidClass: "",
                                eleValidClass: ""
                            }),
                            submitButton: new FormValidation.plugins.SubmitButton()
                        }
                    })
                    .on('core.form.valid', function () {
                        $.ajax({
                            url: '/usuario/grabarpersona',
                            type: 'POST',
                            data: $(form).serialize(),
                            success: function (res) {
                                if (res.success) {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Persona Registrada',
                                        text: res.message
                                    }).then(() => {
                                        $('#CrearPersona').modal('hide');
                                        $('#personasTable').DataTable().ajax.reload();
                                    });
                                } else{
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error Persona Registrada',
                                        text: res.message
                                    }).then(() => {
                                        $('#CrearPersona').modal('hide');
                                    });
                                }
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
}