var BandejaUsuarioEvent = {

    init: function () {
        this.loadUsuariosTable();
        this.loadDropdowns();    
        this.bindEvents();
        this.formvalidator();
        this.formvalidatorgenerico();
        this.formvalidatorpassword();        
    },
    loadUsuariosTable: function () {
        $('#usuariosTable').DataTable({
            ajax: {
                url: '/usuario/api/usuarios',
                dataSrc: ''
            },
            dom: 'frtip',
            columns: [
                { data: 'id_usuario'},
                { data: 'username'},
                { data: 'nombres_completos',
                    render: function (data, type, row) {
                        if (row.nombres_completos!= null){
                            return row.nombres_completos;
                        }
                        else{
                            return '';
                        }
                    }
                },
                { data: 'tipo_documento_texto',
                    render: function (data, type, row) {
                        if (row.numero_documento!= null){
                            return row.tipo_documento_texto+": "+row.numero_documento;
                        }
                        else{
                            return '';
                        }
                    }
                },
                { data: 'correo' },
                { data: 'rol' },
                { data: 'nombre_red' },
                { data: 'nombre_ipress' },
                { data: 'fecha_registro' },
                {
                    data: 'id_usuario',
                    render: function (data, type, row) {
                        if (row.activo)
                            str_allow='<i class="fa fa-lock-open text-success" aria-hidden="true"></i>';
                        else
                            str_allow='<i class="fa fa-lock text-danger" aria-hidden="true"></i>';
                        return str_allow;
                    }
                },
                {
                    data: null,
                    render: function (data, type, row) {
                        if ((row.id_rol==ROLES["ROL_EVALUADOR_IPRESS"]) || (row.id_rol==ROLES["ROL_EVALUADO_IPRESS"])) {
                            bs_target = "#CrearUsuarioGenerico";
                            btn_edit_class = "btn-editar-user-generico";
                        }
                        else {
                            bs_target = "#CrearUsuarioGeneral";
                            btn_edit_class = "btn-editar-user-general";
                        }
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul ${btn_edit_class}" 
                        data-id="${row.id_usuario}" data-bs-toggle="modal" data-bs-target="${bs_target}" data-tipo="edit" >
                        <i class="fas fa-edit"></i> Editar </button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul ${btn_edit_class}"
                        data-id="${row.id_usuario}" data-bs-toggle="modal" data-bs-target="${bs_target}" data-tipo="ver" >
                        <i class="fas fa-eye"></i> Ver </button>`;
                        btn_change_pwd=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-change-pwd"
                        data-id="${row.id_usuario}" data-bs-toggle="modal" data-bs-target="#CambiarPasswordUsuario" >
                        <i class="fas fa-key"></i> Cambiar contraseña </button>`;                           
                        return  btn_edit + btn_view + btn_change_pwd;
                    },
                    orderable: false,
                    searchable: true
                }
            ],
            responsive: true,
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    },
    loadDropdowns: function () {

        $.ajax({
            url: '/dashboard/api/redes',
            type: 'GET',
            success: function (data) {
                const selectRed = $('#sel_red');
                const selectRedAgregadas = $('#sel_redes_asignadas');
                selectRed.empty();
                selectRedAgregadas.empty();                
                data.forEach(r => {
                    selectRed.append(new Option(r.nombre_red, r.id_red));
                    selectRedAgregadas.append(new Option(r.nombre_red, r.id_red));
                });
                selectRedAgregadas.select2({
                    placeholder: "Seleccione una o más redes",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar redes');
            }
        });

        $.ajax({
            url: '/dashboard/api/ipress',
            type: 'GET',
            success: function (data) {
                const selectIpress = $('#sel_ipress');
                selectIpress.empty();
                data.forEach(r => {
                    selectIpress.append(new Option(r.nombre_ipress, r.id_ipress));
                });
                selectIpress.select2({
                    placeholder: "Seleccione Ipress",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar ipress');
            }
        });

        $.ajax({
            url: '/usuario/api/personas',
            type: 'GET',
            success: function (data) {
                const selectPersonas = $('#select_persona');
                selectPersonas.empty();                
                data.forEach(r => {
                    str_opcion = r.tipo_documento_texto+":  "+r.numero_documento+"  -  "+r.nombres_completos;
                    selectPersonas.append(new Option(str_opcion, r.id_persona));
                });
                selectPersonas.select2({
                    placeholder: "Selecciona persona",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar redes');
            }
        });

    },
    bindEvents: function () {

        $('#sel_rol_essalud').on('change', function () {
           rol_seleccionado = $(this).val();
           if (rol_seleccionado==ROLES["ROL_RED"]){
                $('#form_nuevo_usuario').find('#div_show_red_asignadas').removeClass('d-block').addClass('d-none');
                $('#form_nuevo_usuario').find('#div_show_red').removeClass('d-none').addClass('d-block');             
           }
           else{
                if (rol_seleccionado==ROLES["ROL_GESTOR_GAMCC"]){
                    $('#form_nuevo_usuario').find('#div_show_red_asignadas').removeClass('d-none').addClass('d-block');
                    $('#form_nuevo_usuario').find('#div_show_red').removeClass('d-block').addClass('d-none');
                } 
                else { 
                    $('#form_nuevo_usuario').find('#div_show_red_asignadas').removeClass('d-block').addClass('d-none');
                    $('#form_nuevo_usuario').find('#div_show_red').removeClass('d-block').addClass('d-none');  
                }
            }    
        });
        
        $('body').on('click','.btn-new-user-general', function () {
            $('#form_nuevo_usuario').find('input:not(:radio), textarea, select').val('');
            $("#form_nuevo_usuario").find("#select_persona").val(null).trigger("change");
            $("#form_nuevo_usuario").find("#sel_redes_asignadas").val(null).trigger("change");
            $("#form_nuevo_usuario").find("#div_show_red").removeClass('d-block').addClass('d-none');
            $("#form_nuevo_usuario").find("#div_show_red_asignadas").removeClass('d-block').addClass('d-none');            
            $('#CrearUsuarioGeneral').find('#fila_password').show();
        });

        $('body').on('click','.btn-editar-user-general', function () {
            let userId = $(this).data('id');
            let mode = $(this).data('tipo');
            $('#CrearUsuarioGeneral').find('#fila_password').hide();
            $.ajax({
                url: `/usuario/api/getusuariogeneral/${userId}`,
                type: 'GET',
                success: function (data) {
                    $('#id_usuario').val(data.id_usuario);
                    $('#username').val(data.usuario);
                    $('#id_persona').val(data.id_persona);
                    $('#nombres').val(data.nombres);
                    $('#apellido_paterno').val(data.apellido_paterno);
                    $('#apellido_materno').val(data.apellido_materno);
                    $('#tipo_documento').val(data.tipo_documento);
                    $('#numero_documento').val(data.numero_documento);
                    $('#correo').val(data.correo);
                    $('#sel_rol_essalud').val(data.id_rol).trigger('change');
                    $('#sel_red').val(data.id_red).trigger('change');                   
                    $('#select_persona').val(data.id_persona).trigger('change'); 
                    $('#sel_redes_asignadas').val(data.redes_asignadas).trigger('change');                
                    if (data.activo)
                        $('input#activo').prop('checked',true);
                    else
                        $('input#inactivo').prop('checked',true);
                },
                error: function () {
                    alert("Error al cargar los datos del usuario");
                }
            });
            if (mode === 'ver') {
                $('#CrearUsuarioGeneral').find('input, select, textarea').prop('disabled', true);
                $('#CrearUsuarioGeneral').find('.modal-footer').hide();
                $('#CrearUsuarioGeneral').find('.modal-title').text('Ver usuario');
            } else {
                $('#CrearUsuarioGeneral').find('input, select, textarea').prop('disabled', false);
                $('#CrearUsuarioGeneral').find('.modal-footer').show();
                $('#CrearUsuarioGeneral').find('.modal-title').text('Editar usuario');
            }
        });

        $('body').on('click','.btn-nuevo-usuario-generico', function () {
            $("#form_nuevo_usuario_generico").find('input:not(:radio), textarea').val('');
            $("#form_nuevo_usuario_generico").find("#sel_rol_essalud_generico").val('').trigger("change");
            $("#form_nuevo_usuario_generico").find("#sel_ipress").val('').trigger("change");
        });

        $('body').on('click','.btn-editar-user-generico', function () {
            let userId = $(this).data('id');
            let mode = $(this).data('tipo');
            $.ajax({
                url: `/usuario/api/getusuariogenerico/${userId}`,
                type: 'GET',
                success: function (data) {
                    $('#id_usuario_generico').val(data.id_usuario);
                    $('#username_generico').val(data.username);
                    $('#correo_generico').val(data.correo);
                    $('#sel_rol_essalud_generico').val(data.id_rol).trigger('change');
                    $('#sel_ipress').val(data.id_ipress).trigger('change');
                    if (data.activo)
                        $('input#activo_ipress').prop('checked',true);
                    else
                        $('input#inactivo_ipress').prop('checked',true);
                },
                error: function () {
                    alert("Error al cargar los datos del usuario");
                }
            });
            if (mode === 'ver') {
                $('#CrearUsuarioGenerico').find('input, select, textarea').prop('disabled', true);
                $('#CrearUsuarioGenerico').find('.modal-footer').hide();
                $('#CrearUsuarioGenerico').find('.modal-title').text('Ver usuario');
            } else {
                $('#CrearUsuarioGenerico').find('input, select, textarea').prop('disabled', false);
                $('#CrearUsuarioGenerico').find('.modal-footer').show();
                $('#CrearUsuarioGenerico').find('.modal-title').text('Editar usuario');
            }

        });

        $('body').on('click','.btn-change-pwd', function () {
            let userId = $(this).data('id');
            $('#id_usuario_change').val(userId);           
        });

        
        $('body').on('click','.btn_cambia_password', function () {
                        $.ajax({
                            url: '/usuario/changepassword',
                            type: 'POST',
                            data: $(form).serialize(),
                            success: function (res) {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Password actualizado',
                                    text: 'La contraseña ha sido actualizada'
                                }).then(() => {
                                    $('#CambiarPasswordUsuario').modal('hide');
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

    },
    formvalidator: function () {
                    const form = document.getElementById("form_nuevo_usuario");
                    const submitButton = document.getElementById("btn_guarda_usuariogeneral");
                    const valida_datos_generales = FormValidation.formValidation(form, {
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
                            },
                            username: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere un nombre de usuario."
                                    },
                                    callback: {
                                        message: "Por favor, ingrese un nombre de usuario valido.",
                                        callback: function (e) {
                                            if (e.value.length > 0)
                                                return s()
                                        }
                                    }
                                }
                            },
                            correo: {
                                validators: {
                                    regexp: {
                                        regexp: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                        message: "El valor no es una dirección de correo electrónico válida."
                                    },
                                    notEmpty: {
                                        message: "Correo electrónico requerido."
                                    }
                                }
                            },
                            password: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la contraseña."
                                    },
                                    callback: {
                                        message: "Por favor, ingrese una contraseña válida.",
                                        callback: function (e) {
                                            if (e.value.length > 0)
                                                return s()
                                        }
                                    }
                                }
                            },
                            "password-repeat": {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la confirmación de la contraseña."
                                    },
                                    identical: {
                                        compare: function () {
                                            return e.querySelector('[name="password"]').value
                                        },
                                        message: "La contraseña y su confirmación no coinciden."
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
                            url: '/usuario/grabarusuariogeneral',
                            type: 'POST',
                            data: $(form).serialize(),
                            success: function (res) {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Usuario Registrado',
                                    text: 'El usuario ha sido actualizado correctamente'
                                }).then(() => {
                                    $('#CrearUsuarioGeneral').modal('hide');
                                    $('#usuariosTable').DataTable().ajax.reload();
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
    },
    formvalidatorgenerico: function () {
                    const form = document.getElementById("form_nuevo_usuario_generico");
                    const submitButton = document.getElementById("btn_guarda_usuariogenerico");
                    const valida_datos_genericos = FormValidation.formValidation(form, {
                        fields: {
                            username: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere un nombre de usuario."
                                    },
                                    callback: {
                                        message: "Por favor, ingrese un nombre de usuario valido.",
                                        callback: function (e) {
                                            if (e.value.length > 0)
                                                return s()
                                        }
                                    }
                                }
                            },
                            correo: {
                                validators: {
                                    regexp: {
                                        regexp: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                        message: "El valor no es una dirección de correo electrónico válida."
                                    },
                                    notEmpty: {
                                        message: "Correo electrónico requerido."
                                    }
                                }
                            },
                            password: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la contraseña."
                                    },
                                    callback: {
                                        message: "Por favor, ingrese una contraseña válida.",
                                        callback: function (e) {
                                            if (e.value.length > 0)
                                                return s()
                                        }
                                    }
                                }
                            },
                            "password-repeat2": {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la confirmación de la contraseña."
                                    },
                                    identical: {
                                        compare: function () {
                                            return e.querySelector('[name="password"]').value
                                        },
                                        message: "La contraseña y su confirmación no coinciden."
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
                            url: '/usuario/grabarusuariogenerico',
                            type: 'POST',
                            data: $(form).serialize(),
                            success: function (res) {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Usuario Registrado',
                                    text: 'El usuario ha sido creado correctamente'
                                }).then(() => {
                                    $('#CrearUsuarioGenerico').modal('hide');
                                    $('#usuariosTable').DataTable().ajax.reload();
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
    },
    formvalidatorpassword: function () {
                    const form = document.getElementById("form_change_password_usuario");
                    const submitButton = document.getElementById("btn_cambia_password");
                    const valida_datos_password = FormValidation.formValidation(form, {
                        fields: {
                            password: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la contraseña."
                                    },
                                    callback: {
                                        message: "Por favor, ingrese una contraseña válida.",
                                        callback: function (e) {
                                            if (e.value.length > 0)
                                                return s()
                                        }
                                    }
                                }
                            },
                            "password-repeat": {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la confirmación de la contraseña."
                                    },
                                    identical: {
                                        compare: function () {
                                            return e.querySelector('[name="password"]').value
                                        },
                                        message: "La contraseña y su confirmación no coinciden."
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
                            url: '/usuario/changepassword',
                            type: 'POST',
                            data: $(form).serialize(),
                            success: function (res) {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Password actualizado',
                                    text: 'El password ha sido actualizado correctamente'
                                }).then(() => {
                                    $('#CambiarPasswordUsuario').modal('hide');
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
}