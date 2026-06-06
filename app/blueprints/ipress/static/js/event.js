var IpressEvent = {

    init: function () {
        this.loadTabla();
        this.loadDropdowns();
        this.bindEvents();
        this.formvalidator();  
    },
    loadTabla: function () {

        let tabla = $("#tablaIpress").DataTable({
            destroy: true,
            ajax: {
                url: "/ipress/lista",
                dataSrc: ""
            },
            searching: true,
            dom: 'frtip',
            columns: [
                { data: "codigo_ipress" },
                { data: "nombre_ipress" },
                { data: "nivel_ipress" },
                { data: "tipo_ipress" },
                { data: "nombre_red" },
                { data: null, 
                    render: function (data, type, row) {
                       if (row.es_activo == 0) {
                            return '<span class="badge bg-danger text-white">Inactivo</span>';
                        } else if (row.es_activo == 1) {
                            return '<span class="badge bg-success text-white">Activo</span>';
                        }
                    }
                },
                {
                    data: null,
                    render: function (data, type, row) {
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-ipress" 
                        data-id="${row.id_ipress}" data-bs-toggle="modal" data-bs-target="#Modal_EditarIpress" data-tipo="edit" >
                        <i class="fas fa-edit"></i> Editar </button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-ipress"
                        data-id="${row.id_ipress}" data-bs-toggle="modal" data-bs-target="#Modal_EditarIpress" data-tipo="ver" >
                        <i class="fas fa-eye"></i> Ver </button>`;                           
                        return  btn_edit + btn_view;
                    }                    
                }
            ],
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    },
    loadDropdowns: function () {

        const selectNivelIpress = $('#sel_nivel_ipress');
        selectNivelIpress.empty();
        selectNivelIpress.append(new Option('I-2','I-2'));
        selectNivelIpress.append(new Option('I-3','I-3'));
        selectNivelIpress.append(new Option('II-1','II-1'));
        selectNivelIpress.append(new Option('II-E','II-E'));
        selectNivelIpress.append(new Option('II-2','II-2'));
        selectNivelIpress.append(new Option('Sin Nivel','SN'));
        selectNivelIpress.append(new Option('I-4','I-4'));
        selectNivelIpress.append(new Option('III-E','III-E'));
        selectNivelIpress.append(new Option('III-1','III-1'));
        selectNivelIpress.append(new Option('III-2','III-2'));
        selectNivelIpress.select2({
            placeholder: "Seleccione nivel de Ipress",
            width: '100%'
        });

        const selectTipoIpress = $('#sel_tipo_ipress');
        selectTipoIpress.empty();
        selectTipoIpress.append(new Option('C.A.P.I','C.A.P.I'));
        selectTipoIpress.append(new Option('C.A.P.II','C.A.P.II'));
        selectTipoIpress.append(new Option('C.A.P.III','C.A.P.III'));
        selectTipoIpress.append(new Option('C.M.','C.M.'));
        selectTipoIpress.append(new Option('CNSR','CNSR'));
        selectTipoIpress.append(new Option('H.','H.'));
        selectTipoIpress.append(new Option('H.I','H.I'));
        selectTipoIpress.append(new Option('H.II','H.II'));
        selectTipoIpress.append(new Option('H.III','H.III'));
        selectTipoIpress.append(new Option('H.IV','H.IV'));
        selectTipoIpress.append(new Option('H.N.','H.N.'));
        selectTipoIpress.append(new Option('INCOR','INCOR'));
        selectTipoIpress.append(new Option('IPO','IPO'));
        selectTipoIpress.append(new Option('P.M.','P.M.'));
        selectTipoIpress.append(new Option('POL.','POL'));
        selectTipoIpress.select2({
            placeholder: "Seleccione tipo de Ipress",
            width: '100%'
        });

        $.ajax({
            url: '/redes/lista',
            type: 'GET',
            success: function (data) {
                const selectRedIpress = $('#sel_red_ipress');
                selectRedIpress.empty();               
                data.forEach(r => {
                    selectRedIpress.append(new Option(r.nombre_red, r.id_red));
                });
                selectRedIpress.select2({
                    placeholder: "Seleccione una red",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar redes');
            }
        });

        $.ajax({
            url: '/ipress/departamentos',
            type: 'GET',
            success: function (data) {
                const selectDepartamento = $('#sel_departamento');
                selectDepartamento.empty();
                data.forEach(r => {
                    selectDepartamento.append(new Option(r.nombre,r.id));
                });
                selectDepartamento.select2({
                    placeholder: "Seleccione un departamento",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar departamento');
            }
        });

    },
    bindEvents: function(){

        function cargarProvincias(idDepartamento) {
            return $.ajax({
                url: '/ipress/provincias/' + idDepartamento,
                type: 'GET'
            });
        }

        function cargarDistritos(idProvincia) {
            return $.ajax({
                url: '/ipress/distritos/' + idProvincia,
                type: 'GET'
            });
        }

        $('#sel_departamento').on('change', function () {
            let idDepartamento = $(this).val();
            $('#sel_provincia').html('<option value="">Seleccione</option>');
            $('#sel_distrito').html('<option value="">Seleccione</option>');
            if (!idDepartamento) {
                return;
            }
            $.ajax({
                url: `/ipress/provincias/${idDepartamento}`,
                type: 'GET',
                success: function (data) {
                    $.each(data, function (i, item) {
                        $('#sel_provincia').append(`<option value="${item.id}">${item.nombre}</option>`);
                    });
                }
            });
        });

        $('#sel_provincia').on('change', function () {
            let idProvincia = $(this).val();
            $('#sel_distrito').html('<option value="">Seleccione</option>');
            if (!idProvincia) {
                return;
            }
            $.ajax({
                url: `/ipress/distritos/${idProvincia}`,
                type: 'GET',
                success: function (data) {
                    $.each(data, function (i, item) {
                        $('#sel_distrito').append(`<option value="${item.id}">${item.nombre}</option>`);
                    });
                }
            });
        });

        $('#Modal_EditarIpress').on('hidden.bs.modal', function () {
            $('.btn-back-gris').trigger('focus');
        });

        $('body').on('click','.btn-nueva-ipress', function () {
            $('#form_edit_ipress').find('input:not(:radio), textarea, select').val('');
            $("#form_edit_ipress").find("#sel_nivel_ipress").val(null).trigger("change");
            $("#form_edit_ipress").find("#sel_tipo_ipress").val(null).trigger("change");
            $("#form_edit_ipress").find("#sel_red_ipress").val(null).trigger("change");
            $("#form_edit_ipress").find("#sel_departamento").val(null).trigger("change");            
            $("#form_edit_ipress").find("#sel_provincia").val(null).trigger("change");
            $("#form_edit_ipress").find("#sel_distrito").val(null).trigger("change");
        });

        $('body').on('click','.btn-edit-ipress', function () {
            let IpressId = $(this).data('id');
            let mode = $(this).data('tipo');
            $.ajax({
                url: `/ipress/${IpressId}`,
                type: 'GET',
                success: function (data) {
                    $('#form_edit_ipress').find('#id_ipress').val(data.id_ipress);
                    $('#form_edit_ipress').find('#codigo_ipress').val(data.codigo_ipress);
                    $('#form_edit_ipress').find('#nombre_ipress').val(data.nombre_ipress);
                    $('#form_edit_ipress').find('#sel_nivel_ipress').val(data.nivel_ipress).trigger('change');
                    $('#form_edit_ipress').find('#sel_tipo_ipress').val(data.tipo_ipress).trigger('change');
                    $('#form_edit_ipress').find('#sel_red_ipress').val(data.id_red).trigger('change');
                    $('#form_edit_ipress').find('#sel_departamento').val(data.id_departamento).trigger('change');
                    cargarProvincias(data.id_departamento)
                        .done(function() {
                            $('#sel_provincia').val(data.id_provincia).trigger('change');
                            cargarDistritos(data.id_provincia)
                                .done(function() {
                                    $('#sel_distrito').val(data.id_distrito);
                                });
                        });
                    if (data.activo)
                        $('input#activo_ipress').prop('checked',true);
                    else
                        $('input#inactivo_ipress').prop('checked',true);
                },
                error: function () {
                    alert("Error al cargar los datos de la Ipress");
                }
            });
            if (mode === 'ver') {
                $('#Modal_EditarIpress').find('input, select, textarea').prop('disabled', true);
                $('#Modal_EditarIpress').find('.modal-footer').hide();
                $('#Modal_EditarIpress').find('.modal-title').text('Ver Ipress');
            } else {
                $('#Modal_EditarIpress').find('input, select, textarea').prop('disabled', false);
                $('#Modal_EditarIpress').find('.modal-footer').show();
                $('#Modal_EditarIpress').find('.modal-title').text('Editar Ipress');
            }
        });


    },
    formvalidator: function () {
                    const form = document.getElementById("form_edit_ipress");
                    const submitButton = document.getElementById("btn_guarda_ipress");
                    const valida_datos_ipress = FormValidation.formValidation(form, {
                        fields: {
                            codigo_ipress: {
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
                        const id = $('#form_edit_ipress').find('#id_ipress').val();
                        const data = {
                            codigo_ipress: $('#codigo_ipress').val(),
                            nombre_ipress: $('#nombre_ipress').val(),
                            nivel_ipress: $('#nivel_ipress').val(),
                            tipo_ipress: $('#sel_tipo_ipress').val(),
                            id_red: $('#sel_red').val(),
                            id_departamento: $('#sel_departamento').val(),
                            id_provincia: $('#sel_provincia').val(),
                            id_distrito: $('#sel_distrito').val()
                        };
                        let method;
                        let url;
                        if (id) {
                            method = 'PUT';
                            url = `/ipress/${id}`;
                        } else {
                            method = 'POST';
                            url = '/ipress';
                        }
                        $.ajax({
                            url: url,
                            type: method,
                            contentType: 'application/json',
                            data: JSON.stringify(data),
                            success: function (response) {
                                $('#Modal_EditarIpress').modal('hide');
                                $('#tablaIpress').DataTable().ajax.reload();
                            },
                            error: function (xhr) {
                                alert("Error al cargar los datos de la Ipress");
                            }
                        });
                    });
    }   
};