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

                        str_adm_condicion =`<button class="btn btn-sm btn-secondary btn-text-azul m-2 btn-add-condicion" data-idcondicion="${data.id_condicion}" data-bs-toggle="modal" data-bs-target="#AddCondicion"><i class="bi bi-list-check"></i></i>Editar Condicion</button>`;
                        str_adm_fuente='';
                        if (data.id_tecnica == 4) {
                              str_adm_fuente =`<button class="btn btn-sm btn-secondary btn-text-azul m-2" data-idcondicion="${data.id_condicion}" data-bs-toggle="modal" data-bs-target="#AdmFuentes"><i class="bi bi-link"></i>Editar Fuentes</button>`;
                        }
                        return str_adm_condicion+str_adm_fuente;
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
        /*Dropzone.autoDiscover = false;
        var dz = null;
        let contador = 1;
        let dropzones = [];

        $("#btnAgregarDropzone").on("click", function() {
            str_add='<div class="dz-message needsclick">'
            +'<i class="bi bi-cloud-arrow-up fs-3x text-primary"></i>'
            +'<div class="fs-3 fw-bold text-gray-900 mb-1">Suelta los archivos aquí o haz clic.</div>'
            +'<div class="fs-6 text-gray-500">Tamaño máximo 20 MB</div>'
            +'</div>';
            const div = document.createElement("div");
            div.id = "dropzone_" + contador;
            div.classList.add("dropzone-dinamico");
            div.innerHTML = str_add;
            $("#contenedorDropzones").append(div);
            //Crea dropzone con ID dinámico
            const dz = new Dropzone("#dropzone_" + contador, {
                url: "/acredita/uploadfile",
                paramName: "file",
                maxFiles: 10,
                maxFilesize: 10,
                addRemoveLinks: true,
                dictDefaultMessage: "Arrastra archivos aquí o haz clic"
            });
            dropzones.push(dz);
            contador++;
        });*/

        $('#AddCondicion').on('show.bs.modal', function (event) {
            console.log('abre el modal');
            const button = $(event.relatedTarget);
            const idCond = button.data('idcondicion');
            const tipo = button.data('tipo');
            console.log('id de condicon '+idCond);
            if (idCond == 0){
                $('#form_nueva_condicion')[0].reset();
                $('#id_condicion').val(0);
                $('#select_tecnica').val(null).trigger('change');
                $('#select_puntaje').val(null).trigger('change');
            } else {
                $.ajax({
                    url: `/acredita/api/condicion/${idCond}`,
                    method: 'GET',
                    dataType: 'json',
                    success: function (data) {
                        $('#id_condicion').val(idCond);
                        $('#nombre_condicion').val(data.nombre_condicion);
                        $('#select_puntaje').val(data.puntaje_condicion).trigger('change');
                        $('#select_tecnica').val(data.id_tecnica).trigger('change');
                    },
                    error: function (xhr, status, error) {
                        console.error('Error al cargar condición:', error);
                    }
                });
            }
            $('.modal-title').text(tipo === 'nuevo' ? 'Nueva condición' : 'Editar condición');
        });


        $('#AdmFuentes').on('show.bs.modal', function (event) {
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
                        $.ajax({
                            url: '/acredita/grabarcondicion',
                            async: false,
                            type: 'POST',
                            contentType: "application/json",
                            data: $(form).serialize(),
                            success: function (res) {
                                if (res.success) {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Condicion Registrada',
                                        text: res.message
                                    }).then(() => {
                                        $('#AddCondicion').modal('hide');
                                        $('#tablaCondiciones').DataTable().ajax.reload();
                                    });
                                } else{
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error Condición Registrada',
                                        text: res.message
                                    }).then(() => {
                                        $('#AddCondicion').modal('hide');
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
                                        $('#AdmFuentes').modal('hide');
                                    });
                                } else{
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error en Grabar Fuentes',
                                        text: res.message
                                    }).then(() => {
                                        $('#AdmFuentes').modal('hide');
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
