var CondicionesEvent = {
    init: function () {
        this.loadCombos();
        this.bindEvents();
        this.loadTabla();
        this.formvalidator();
        this.formvalidator2();
    },
    loadTabla: function () {
        if ($.fn.DataTable.isDataTable('#tablaCondiciones')) {
                $('#tablaCondiciones').DataTable().clear().destroy();
        }        
        $('#tablaCondiciones').DataTable({
            ajax: {
                url: `/acredita/api/condiciones/${idCriterio}`,
                dataSrc: ''
            },
            columnDefs: [
                {
                    targets: 5,
                    width: "120px",
                    className: "text-nowrap"
                },
                {
                    targets: 6,
                    width: "120px",
                    className: "text-nowrap"
                }
            ],
            columns: [
                { data: 'id_condicion'},
                { data: 'nombre_condicion'},
                { data: 'puntaje_condicion' },
                { data: 'nombre_tecnica' },
                {
                    data: "fuentes",
                    render: function (fuentes) {
                        if (!fuentes || fuentes.length === 0) {
                            return "<span class='text-muted'>Sin fuentes</span>";
                        }
                        let html = "";
                        fuentes.forEach(f => {
                            html += ``
                            if (f.link_fuente)
                                html += `${f.nombre_fuente}&nbsp;<a href="${f.link_fuente}" target="_blank" class="d-block"><i class="bi bi-file-earmark-arrow-down-fill fs-2 text-success"></i></a>`;
                            else
                                html += `${f.nombre_fuente}`;
                        });
                        return html;
                    }
                },
                {
                    data: null,
                    render: function(data) {
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-add-condicion" data-idcondicion="${data.id_condicion}" data-bs-toggle="modal" data-bs-target="#Modal_AddCondicion" data-tipo="edit" >
                        <i class="fas fa-edit"></i>Editar</button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-add-condicion" data-idcondicion="${data.id_condicion}" data-bs-toggle="modal" data-bs-target="#Modal_AddCondicion" data-tipo="ver" >
                        <i class="fas fa-eye"></i>Ver</button>`;                           
                        return  btn_edit + '&nbsp;&nbsp;' + btn_view;
                    }
                },
                {
                    data: null,
                    render: function(data) {
                        str_adm_fuente='';
                        if (data.id_tecnica == 4) {
                              str_adm_fuente =`<button class="btn btn-sm btn-secondary btn-text-azul btn-add-fuentes" data-idcondicion="${data.id_condicion}" data-bs-toggle="modal" data-bs-target="#Modal_AddFuentes"><i class="bi bi-link"></i>Editar Fuente</button>`;
                        }
                        return str_adm_fuente;
                    }
                }                 
            ],
            responsive: true,
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    },
    loadCombos: function () {
        const selectPuntaje = $('#select_puntaje');
        selectPuntaje.select2({
                    placeholder: "Selecciona puntaje",
                    width: '100%',
                    allowClear: true
                });

        $.ajax({
            url: '/acredita/api/tecnicas',
            type: 'GET',
            success: function (data) {
                const selectTecnica = $('#select_tecnica');
                selectTecnica.empty();              
                data.forEach(r => {
                    selectTecnica.append(new Option(r.nombre, r.id_tecnica));
                });
                selectTecnica.select2({
                    placeholder: "Selecciona técnica",
                    width: '100%',
                    allowClear: true
                });
            },
            error: function () {
                console.error('Error al cargar tecnicas');
            }
        });
    
    },
    bindEvents: function () {

        $('body').on('click','.btn-add-condicion', function () {
            const idCriterio = $('#id_criterio').val();
            const idCondicion = $(this).data('idcondicion');
            const tipo = $(this).data('tipo');
            if (tipo=="nuevo"){
                $('#form_nueva_condicion').find('input:not(:radio), textarea, select').val('');
                $("#form_nueva_condicion").find("#select_puntaje").val(null).trigger("change");
                $("#form_nueva_condicion").find("#select_tecnica").val(null).trigger("change");
                $("#form_nueva_condicion").find("#tipo_condicion").val(null).trigger("change");
            } else {
                $('#form_nueva_condicion').find('#select_puntaje')
                $.ajax({
                    url: `/acredita/api/condicion/${idCondicion}`,
                    method: 'GET',
                    dataType: 'json',
                    success: function (data) {     
                            $('#form_nueva_condicion').find('#id_criterio').val(idCriterio);
                            $('#form_nueva_condicion').find('#id_condicion').val(idCondicion);                                               
                            $('#form_nueva_condicion').find('#nombre_condicion').val(data.nombre_condicion);
                            $('#form_nueva_condicion').find('#select_puntaje').val(data.puntaje_condicion).trigger('change');
                            $('#form_nueva_condicion').find('#select_tecnica').val(data.id_tecnica).trigger('change');
                            $('#form_nueva_condicion').find('#normativa_condicion').val(data.normativa_condicion);
                            $('#form_nueva_condicion').find('#link_normativa').val(data.link_normativa);
                            $('#form_nueva_condicion').find('#tipo_condicion').val(data.tipo_condicion).trigger('change');                        
                    },
                    error: function (xhr, status, error) {
                        console.error('Error al cargar condición:', error);
                    }
                });
                $('.modal-title').text(tipo === 'nuevo' ? 'Nueva condición' : 'Editar condición');
                if (tipo === 'ver') {
                    $('#Modal_AddCondicion').find('input, select, textarea').prop('disabled', true);
                    $('#Modal_AddCondicion').find('.modal-footer').hide();
                    $('#Modal_AddCondicion').find('.modal-title').text('Ver Condicion');
                } else {
                    $('#Modal_AddCondicion').find('input, select, textarea').prop('disabled', false);
                    $('#Modal_AddCondicion').find('.modal-footer').show();
                    $('#Modal_AddCondicion').find('.modal-title').text('Editar Condicion');
                }
            }
        });

        $('#Modal_AddCondicion').on('hidden.bs.modal', function () {
            document.activeElement.blur();
        });

        $('body').on('click','.btn-add-fuentes', function () {
            const button = $(event.relatedTarget);
            const idCond = button.data('idcondicion');
            $('#form_update_fuentes').find('#id_condicion').val(idCond);
            $("#tablaFuentes tbody").empty();
            $.ajax({
                url: `/acredita/api/fuentes/${idCond}`,
                success: function (data) {
                    data.forEach(function (f) {
                        let fila = `<tr>
                                    <td><input type="hidden" class="form-control id_fuente" value="${f.id_fuente}">
                                    <input type="text" class="form-control nombre_fuente" value="${f.nombre_fuente}"></td>
                                    <td><input type="text" class="form-control link_fuente" value="${f.link_fuente}"></td>
                                    <td><button class="btn btn-danger btn-sm btnEliminar"><i class="fa fa-trash"></i></button></td>
                                </tr>`;
                        $("#tablaFuentes tbody").append(fila);
                    });
                }
            });
            let nuevaFila = `<tr>
                <td><input type="hidden" class="form-control id_fuente" />
                <input type="text" class="form-control nombre_fuente" /></td>
                <td><input type="text" class="form-control link_fuente" /></td>
                <td><button class="btn btn-danger btn-sm btnEliminar"><i class="fa fa-trash"></i></button></td>
            </tr>`;
            $("#tablaFuentes tbody").append(nuevaFila);
        });
        

        $("#tablaFuentes").on("click", ".btnAgregarFila", function () {
            console.log('en add fila');
            let nuevaFila = `<tr>
                <td><input type="hidden" class="form-control id_fuente" />
                <input type="text" class="form-control nombre_fuente" /></td>
                <td><input type="text" class="form-control link_fuente" /></td>
                <td><button class="btn btn-danger btn-sm btnEliminar"><i class="fa fa-trash"></i></button></td>
            </tr>`;
            $("#tablaFuentes tbody").append(nuevaFila);
        });


        $("#tablaFuentes").on("click", ".btnEliminar", function () {
            $(this).closest("tr").remove();
        });
    },
    formvalidator: function () {
                    const form = document.getElementById("form_nueva_condicion");
                    const submitButton = document.getElementById("btn_guarda_condicion");
                    const valida_datos_persona = FormValidation.formValidation(form, {
                        fields: {
                            "select_puntaje": {
                                validators: {
                                    notEmpty: {
                                        message: "Indique el puntaje"
                                    }
                                }
                            },
                            "select_tecnica": {
                                validators: {
                                    notEmpty: {
                                        message: "Indique la técnica"
                                    }
                                }
                            },
                            "nombre_condicion": {
                                validators: {
                                    notEmpty: {
                                        message: "Indique el nombre de la condición"
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
                        let method;
                        let url;
                        const id = $('#form_nueva_condicion').find('#id_criterio').val();
                        if (id) {
                            method = 'PUT';
                            url = `/acredita/condicion/${id}`;
                        } else {
                            method = 'POST';
                            url = '/acredita/condicion';
                        }
                        $.ajax({
                            url: url,
                            type: method,
                            data: $(form).serialize(),
                            success: function (res) {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Condicion Actualizada',
                                    text: 'Condicion ha sido actualizado correctamente'
                                }).then(() => {
                                    $('#Modal_AddCondicion').modal('hide');
                                    $('#tablaCondiciones').DataTable().ajax.reload();
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
    formvalidator2: function (){
                    const form2 = document.getElementById("form_update_fuentes");
                    const submitButton2 = document.getElementById("btn_guarda_fuentes");
                    const valida_fuentes = FormValidation.formValidation(form2, {
                        fields: {
                            // se registrarán dinámicamente
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
                        id_condicion= $('#form_update_fuentes').find('#id_condicion').val();
                        datos =[];
                        $("#tablaFuentes tbody tr").each(function () {
                            let id_fuente = $(this).find(".id_fuente").val();
                            let nombre = $(this).find(".nombre_fuente").val();
                            let link = $(this).find(".link_fuente").val();
                            console.log(id_fuente+nombre+link);
                            if (nombre !== "" || link !== "") {
                                datos.push({
                                    id_fuente: id_fuente,
                                    nombre_fuente: nombre,
                                    link_fuente: link,
                                    id_condicion: id_condicion 
                                });
                            }
                        });
                        $.ajax({
                            url: '/acredita/grabarfuentes',
                            async: false,
                            type: 'POST',
                            contentType: "application/json",
                            data: JSON.stringify(datos),
                            success: function (res) {
                                console.log(datos);
                                if (res.success) {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Fuentes Registrada',
                                        text: res.message
                                    }).then(() => {
                                        $('#Modal_AddFuentes').modal('hide');
                                    });
                                } else{
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error en Grabar Fuentes',
                                        text: res.message
                                    }).then(() => {
                                        $('#Modal_AddFuentes').modal('hide');
                                    });
                                }
                                $('#tablaCondiciones').DataTable().ajax.reload();
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
