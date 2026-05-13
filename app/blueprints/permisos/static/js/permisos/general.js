var BandejaPermisosEvent = {

init: function () {
        this.loadPermisosTable();
        this.loadDropdowns();
        this.bindEvents();
        this.formvalidator();
    },
    loadPermisosTable: function () {
        $('#permisosTable').DataTable({
            ajax: {
                url: '/permisos/api/getlistaroles',
                dataSrc: ''
            },
            columns: [
                { data: 'id_rol'},
                { data: 'nombre_rol'},
                { data: 'opciones_rol'},
                {
                    data: null,
                    render: function (data, type, row) {
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-permisos" 
                        data-id="${row.id_rol}" data-name="${row.nombre_rol}" data-opciones="${row.arr_opciones}" data-bs-toggle="modal" data-bs-target="#AsignarOpcionRol" data-tipo="edit" >
                        <i class="fas fa-edit"></i> Editar </button>`;                          
                        return  btn_edit;
                    },
                    orderable: false,
                    searchable: false
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
            url: '/permisos/api/getallopciones',
            type: 'GET',
            success: function (data) {
                const selectOpciones = $('#sel_opciones');
                selectOpciones.empty();                
                data.forEach(r => {
                    selectOpciones.append(new Option(r.opciones_rol,r.id_opcion));
                });
                selectOpciones.select2({
                    placeholder: "Selecciona opcion",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar opciones');
            }
        });
    },
    bindEvents: function () {
        $('body').on('click','.btn-edit-permisos', function () {
            let rolId = $(this).data('id');
            let nombreRol = $(this).data('name');
            let opciones = $(this).data('opciones');
            $('#id_rol').val(rolId);
            $('#nombre_rol').val(nombreRol);
            $('#sel_opciones').val(null).trigger('change');
            console.log(opciones);
            $('#sel_opciones').val(null).trigger('change');
            if (opciones !== null) {
                const valores = opciones.toString().split(';');
                $('#sel_opciones').val(valores).trigger('change');
            }
            
        });
    },
    formvalidator: function(){
                    const form = document.getElementById("form_asignar_opcion_rol");
                    const submitButton = document.getElementById("btn_guarda_opciones");
                    const valida_datos = FormValidation.formValidation(form, {
                        fields: {
                            nombre_rol: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere el rol."
                                    }
                                }
                            }                            
                        },
                        plugins: {
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
                            url: '/permisos/grabaropciones',
                            type: 'POST',
                            data: $(form).serialize(),
                            success: function (res) {
                                if (res.success) {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Opciones Actualizadas',
                                        text: res.message
                                    }).then(() => {
                                        $('#AsignarOpcionRol').modal('hide');
                                        $('#permisosTable').DataTable().ajax.reload();
                                    });
                                } else{
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error Opciones Actualizadas',
                                        text: res.message
                                    }).then(() => {
                                        $('#AsignarOpcionRol').modal('hide');
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
};