var EvaluadorCalificarEvent = {

    init: function () {
        this.pintarPuntaje();
        this.loadTabla();        
        this.bindEvents();
        this.formValidator();
    }, 
    pintarImagen: function(file) {

        if (!file || !file.previewElement) return;
        file.previewElement.addEventListener("click", function(e) {
            if (e.target.classList.contains("dz-remove")) return;
            let url = "";
             if (file.dataURL) {
                url = file.dataURL;
            } else{         
                url = "/uploads/fuentes/" + file.server_name.replace(/\\/g, "/") + "?t=" + Date.now();
            }
            if (!url) {
                console.warn("No hay URL para este archivo", file);
                return;
            }
            $("#previewImage").attr("src", url);
            $("#modalPreview").modal("show");
        });
    },
    pintarPuntaje: function(puntaje){

        if (puntaje === 0){
            return `<div class="symbol-label fs-2x fw-semibold text-danger bg-light-danger p-3">PUNTAJE:&nbsp;0</div>`;
        }
        if (puntaje === 1){
            return `<div class="symbol-label fs-2x fw-semibold text-warning bg-light-warning p-3">PUNTAJE:&nbsp;1</div>`;
        }
        if (puntaje === 2){
            return `<div class="symbol-label fs-2x fw-semibold text-success bg-light-success p-3">PUNTAJE:&nbsp;2</div>`;
        }
        return `<div class="symbol-label fs-2x fw-semibold text-secondary bg-light-secondary p-3">PUNTAJE:&nbsp;Sin Calificar</div>`;
    },
    loadTabla: function () {

        id_criterio = $('#id_criterio').val();
        $('#id_criterio_calcular').val(id_criterio);
        let puntaje_final = 0;
        $.ajax({
            url: `evaluacion/api/getpuntajecriterio/${id_criterio}/id_ae/${IdAutoevaluacion}`,
            type: "GET",
            success: function (res) {
                puntaje_final = res.puntaje_criterio;
            }
        });

        let boton_grabar = 1;
        let select_puntajes2 = '';
        let tabla = $("#tbl_evaluador_reporte").DataTable({
            destroy: true,
            ajax: {
                url: `evaluacion/api/getevaluadorreporte/`+id_criterio+'/id_ae/'+IdAutoevaluacion,
                dataSrc: function(json){
                    boton_grabar = json.boton_grabar;
                    select_puntajes2 = json.select_puntajes2;
                    return json.data;
                }           
            },
            rowGroup: {
                dataSrc: 'nombre_condicion',
                startRender: function (rows, group) {
                        let idCondicion = rows.data()[0].id_condicion;                    
                        let puntajeCondicion = rows.data()[0].puntaje_condicion;
                        let tipoCondicion = rows.data()[0].tipo_condicion;
                        let tecnicaCondicion = rows.data()[0].id_tecnica;
                        return `<span>CONDICION A CUMPLIR: ${group}</span>
                            <input type="hidden" name="condicion_`+idCondicion+`" class="idGrupoHidden" value="${idCondicion}">
                            <input type="hidden" name="puntaje_condicion_`+idCondicion+`" class="idGrupoHidden" value="${puntajeCondicion}">
                            <input type="hidden" name="tipo_condicion_`+idCondicion+`" class="idGrupoHidden" value="${tipoCondicion}">
                            <input type="hidden" name="tecnica_condicion_`+idCondicion+`" class="idGrupoHidden" value="${tecnicaCondicion}">
                            <input type="hidden" name="puntaje_real_condicion_`+idCondicion+`" class="idGrupoHidden" value="">`        
                    }
            },
            columns: [
                { data: "nombre_tecnica"
                 },
                { data: "nombre_fuente"
                 },
                { data: null,
                    render: function (data, type, row) {
                        console.log(row.id_tecnica);
                        /* tipo_reporte 1:archivo 2:link*/
                        if (row.id_tecnica == '4') {
                            boton_fuente = 'no reportado';
                            if (row.tipo_reporte == '1') {
                               /*boton_fuente = '<a class="btn btn-primary" href="/uploads/fuentes/' + row.rep_ruta_archivo + '" target="_blank">VER</a>';*/
                                boton_fuente = '<a href="/uploads/fuentes/' + row.rep_ruta_archivo + '" target="_blank" class="text-success"><i class="text-success bi bi-cloud-arrow-up me-1"></i>Fuente Cargada</a>';
                            } 
                            else if (row.tipo_reporte == '2') {
                                /*boton_fuente = '<a class="btn btn-primary" href="' + row.rep_link_reporte + '" target="_blank">VER</a>';*/
                                boton_fuente = '<a href="#" class="text-info" target="_blank">Link externo <i class="text-info bi bi-box-arrow-up-right ms-1"></i></a>';
                            } 
                            else if (row.link_fuente !== null && row.link_fuente !== '') {
                                boton_fuente = '<a class="btn text-primary" href="' + row.link_fuente + '" target="_blank">Predefinida</a>';
                            }
                        } else if (row.id_tecnica == '3') {
                            boton_fuente='<input type="hidden" class="filesToInsertDB" id="filesToInsertDB_'+row.id_condicion+'" name="filesToInsertDB_'+row.id_condicion+'">';
                            boton_fuente+='<div class="dropzone" id="dropzone_'+row.id_condicion+'" >';                            
                            boton_fuente+='<div class="dz-message needsclick">';
                            boton_fuente+='<i class="ki-duotone ki-file-up fs-3x text-primary"><span class="path1"></span><span class="path2"></span></i>';
                            boton_fuente+='<div class="ms-4">';
                            boton_fuente+='<h3 class="fs-5 fw-bold text-gray-900 mb-1">Drop files here or click to upload.</h3>';
                            boton_fuente+='<span class="fs-7 fw-semibold text-gray-500">Upload up to 10 files</span>';
                            boton_fuente+='</div>';
                            boton_fuente+='</div>';
                            boton_fuente+='</div>';
                        }
                        else {
                            boton_fuente = 'no aplica reporte';
                        }
                        return boton_fuente;
                    }
                },
                { data: null,
                  className: "d-flex align-items-center",
                    render: function (data, type, row) {
                        return row.checks+'&nbsp;&nbsp;'+row.select_observaciones+row.valor_fuente;
                    }
                }    
            ],
            columnDefs: [
                {
                    targets: 3,
                    className: 'dt-nowrap'
                }
            ],
            drawCallback: function () {

                Dropzone.autoDiscover = false;
                $('#form_calcular_puntaje_criterio').find('#califica_puntaje_2').html(select_puntajes2);
                if ($('#form_calcular_puntaje_criterio').find('#es_precalificado').val() === 'True' || boton_grabar == 0) {
                    $('#grabar_puntaje_criterio').hide();
                    if ($('#form_calcular_puntaje_criterio').find('#regla_puntaje2_1condicion').val()=='true'){
                        $('.select_fuente_value').prop('disabled', true);
                    }
                }
                /** Apagar el boton grabar si el puntaje es cero, es decir no tiene archivos reportados */
                if ($('#form_calcular_puntaje_criterio').find("#puntaje_actual_criterio").val() === '0') {
                    $.ajax({
                        url: `/evaluacion/validarpuntajecero/${id_criterio}/${IdAutoevaluacion}`,
                        type: "GET",
                        dataType: "json",
                        success: function(response){
                            if(response.cumple){
                                $('#grabar_puntaje_criterio').hide();
                                if ($('#form_calcular_puntaje_criterio').find('#regla_puntaje2_1condicion').val()=='true'){
                                        $('.select_fuente_value').prop('disabled', true);
                                }
                            }else{
                                $('#grabar_puntaje_criterio').show();
                            }
                        },
                        error: function(error){
                            console.error("Error en la consulta", error);
                        }
                    });
                }
                $('#texto_puntaje').html(EvaluadorCalificarEvent.pintarPuntaje(puntaje_final));
                $('.select_fuente_value').val(puntaje_final).trigger('change');


                $('#form_calcular_puntaje_criterio .dropzone').each(function() {
                    
                    let dropzoneId = this.id;       
                    let idCondicion = dropzoneId.replace('dropzone_', '');
                    let inputId = 'filesToInsertDB_' + idCondicion;
                    let rowData = tabla.row($(this).closest('tr')).data();

                    let myDropzone = new Dropzone('#'+dropzoneId, {
                        url: '/auth/uploadevidencia',
                        paramName: "file",                        
                        parallelUploads: 5,
                        maxFiles: 2,
                        maxFilesize: 1, // MB
                        addRemoveLinks: true,
                        autoProcessQueue: false,
                        acceptedFiles: ".jpg",
                        dictFileTooBig: "El archivo es demasiado grande ({{filesize}}MB). Máx: {{maxFilesize}}MB.",
                        dictDefaultMessage: "Seleccione el archivo de autorización",
                        init: function() {

                            let myDropzone = this;
                            let filesInput = [];
                            if (rowData.id_tecnica == 3 && rowData.archivos) {
                                rowData.archivos.forEach(file => {
                                    let mockFile = {
                                        name: file.nombre,
                                        size: 12345,                                        
                                        server_name: file.upload_filename,
                                        isNew: false
                                    };
                                    let url = "/" + file.ruta.replace(/\\/g, "/") + "?t=" + Date.now();                                    
                                    myDropzone.emit("addedfile", mockFile);
                                    myDropzone.emit("thumbnail", mockFile, url);
                                    myDropzone.emit("success", mockFile); 
                                    myDropzone.emit("complete", mockFile);
                                    console.log(mockFile);
                                    EvaluadorCalificarEvent.pintarImagen(mockFile);
                                    myDropzone.files.push(mockFile);
                                    filesInput.push({
                                        real_filename: file.nombre,
                                        upload_filename: file.upload_filename
                                    });
                                    });
                                $(`#filesToInsertDB_${rowData.id_condicion}`).val(JSON.stringify(filesInput));
                            }
                            this.on("addedfile", function(file) {
                               EvaluadorCalificarEvent.pintarImagen(file);
                            });

                            this.on("success", function(file, response) {
                                if (response) {
                                    file.real_name = response.real_filename;
                                    file.server_name = response.upload_filename;
                                    file.isNew = true; 
                                    let current = $('#'+inputId).val();
                                    let files = current ? JSON.parse(current) : [];
                                    files.push({
                                        real_filename: response.real_filename,
                                        upload_filename: response.upload_filename
                                    });
                                    $('#'+inputId).val(JSON.stringify(files));
                                    console.log("Archivos actuales:", files);
                                }
                            });

                            this.on("removedfile", function(file) {

                                let input = $(`#filesToInsertDB_${rowData.id_condicion}`);
                                console.log(input);
                                console.log("input encontrado:", input.length);
                                let files = input.val() ? JSON.parse(input.val()) : [];
                                console.log("Antes:", files);
                                console.log("server_name:", file.server_name);
                                files = files.filter(f => f.upload_filename !== file.server_name);
                                input.val(JSON.stringify(files));
                                console.log("Después:", files);

                                if (file.server_name && file.isNew) {

                                    $.ajax({
                                        url: `/auth/delete-evidencia/${file.server_name}`,
                                        type: "DELETE",
                                        success: function() {
                                            console.log("Archivo temporal eliminado");
                                        },
                                        error: function(err) {
                                            console.error("Error eliminando temp:", err);
                                        }
                                    });

                                }

                            });


                        }
                    });

                });

            },
            language: {
                url: "/static/json/es-ES.json"
            },
            paging: false,
            searching: false,
            info: false,
            order: [[0, 'asc']]
        });

    },
    bindEvents: function (){

        function cargarTiposObservacion(id_fuente){
            $.ajax({
            url: "/evaluacion/api/gettiposobservaciones",
            type: "GET",
            dataType: "json",
            success: function(data){
                    let html = `<select name="tipoObservacion_${id_fuente}"  id="tipoObservacion_${id_fuente}" class="select_observacion form-select form-select-sm w-auto">`;
                    html += `<option value="">Seleccione</option>`;
                    $.each(data, function(i, item){
                        html += `<option value="${item.id}">${item.nombre}</option>`;
                    });
                    html += `</select>`;
                    $(`#set_select_observaciones_${id_fuente}`).html('');
                    $(`#set_select_observaciones_${id_fuente}`).html(html);
                },
                error: function(){
                    console.log("Error cargando tipos de observación");
                }
            });
        }

        $(document).on("click", "a.btn_approve", function () {
            console.log('aprove')
            input_def = $(this).find('i');
            input_def.removeClass("text-muted").addClass("text-success");
            $(this).parent().find('a.btn_disapprove i').removeClass("text-danger").addClass("text-muted");
            $(this).parent().find(".valor_set").val("1");
            let id_fuente = $(this).find("i").data("idfuente");
            $(this).parent().find(`#set_select_observaciones_${id_fuente}`).html('');
        });

        $(document).on("click", "a.btn_disapprove", function () {
            input_dis= $(this).find('i');
            input_dis.removeClass("text-muted").addClass("text-danger");
            $(this).parent().find('a.btn_approve i').removeClass("text-success").addClass("text-muted");
            $(this).parent().find(".valor_set").val("0");
            /**** Solo si es tecnica 4, debo cargar el desplegable de observaciones ***/
            let id_fuente = $(this).find("i").data("idfuente");
            console.log("Fuente:", id_fuente);
            cargarTiposObservacion(id_fuente);
        });


        $(document).on("click", ".select_fuente_value", function () {
            val_to_set = $(this).val();
            $(this).parent().find(".valor_set").val(val_to_set);
        });


    },
    formValidator: function (){

        function calcular_puntaje_del_criterio() {

            if ($('#regla_puntaje2_1condicion').val()=='true')
            {
                puntaje_final_criterio = 0;
                $('select[name^="valor_"]').each(function () {
                    puntaje_final_criterio += parseFloat($(this).val()) || 0;
                });
            }
            else {
                $('input[name^="condicion_"]').each(function () { /* iterar para todas las condiciones */
                    const name = $(this).attr('name');
                    const id_condicion = name.split('_')[1];
                    tecnica = $('input[name^="tecnica_condicion_'+id_condicion+'"]').val();
                    tipo_condicion = $('input[name^="tipo_condicion_'+id_condicion+'"]').val();
                    puntaje_condicion =  $('input[name^="puntaje_condicion_'+id_condicion+'"]').val();
                    //En el caso que la tecnica sea revision documentaria
                    if (tecnica == '4'){
                        
                        prefijo_inputs_condicion = 'valor_'+id_condicion;
                        if (tipo_condicion == 'Y'){
                            let valor_and = true;
                            $('input[name^="'+prefijo_inputs_condicion+'"]').each(function () {
                                console.log('valores...'+$(this).val());
                                if ($(this).val()=='0'){
                                    valor_and = false;
                                }
                            });
                            if (valor_and) $('input[name^="puntaje_real_condicion_'+id_condicion+'"]').val(puntaje_condicion);
                            else  $('input[name^="puntaje_real_condicion_'+id_condicion+'"]').val(0);                        
                        }
                        else 
                            if (tipo_condicion == 'O'){                        
                                let valor_or = false;
                                $('input[name^="'+prefijo_inputs_condicion+'"]').each(function () {
                                    if ($(this).val()=='1') {
                                        valor_or = true;
                                    }
                                });                           
                                if (valor_or) $('input[name^="puntaje_real_condicion_'+id_condicion+'"]').val(puntaje_condicion);
                                else  $('input[name^="puntaje_real_condicion_'+id_condicion+'"]').val(0); 
                        }
                        else{
                            ptje_real = $('input[name^="'+prefijo_inputs_condicion+'"]').val();
                            $('input[name^="puntaje_real_condicion_'+id_condicion+'"]').val(ptje_real);
                        }
                    }/* fin de tecnica 4*/
                    else{
                            ptje_real = $('input[name^="valor_'+id_condicion+'"]').val();
                            $('input[name^="puntaje_real_condicion_'+id_condicion+'"]').val(ptje_real);
                    }
                });
                /*Barrer todos los inputs de los valores finales de las condiciones y sumarlos para hallar el puntaje final del criterio  */
                puntaje_final_criterio = 0;
                $('input[name^="puntaje_real_condicion_"]').each(function () {
                    puntaje_final_criterio += parseFloat($(this).val()) || 0;
                });
            }
            $('#texto_puntaje').html(EvaluadorCalificarEvent.pintarPuntaje(puntaje_final_criterio))
            $('#puntaje_total_criterio').val(puntaje_final_criterio);
        }

        const form = document.getElementById("form_calcular_puntaje_criterio");
        const submitButton = document.getElementById("grabar_puntaje_criterio");        
        const calcula_puntaje = FormValidation.formValidation(form, {
                        fields: {
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

                        let resultado = [];
                        $('#form_calcular_puntaje_criterio .filesToInsertDB').each(function() {
                            let input = this;
                            let idCondicion = input.id.replace('filesToInsertDB_', '');
                            if (input.value) {
                                try {
                                    let files = JSON.parse(input.value);
                                    resultado.push({
                                        id_condicion: parseInt(idCondicion),
                                        files: files
                                    });
                                } catch (e) {
                                    console.error("Error JSON:", input.value);
                                }
                            }
                        });
                        console.log("FINAL A ENVIAR:", resultado);
                        $('#form_calcular_puntaje_criterio').find('#filesToSend').val(JSON.stringify(resultado));
                        let fuentes = [];
                        let condiciones = [];
                        calcular_puntaje_del_criterio();
                        $('#form_calcular_puntaje_criterio').find('.valor_set').each(function () {
                            if ($(this).attr('data-tecnica') === '4') {
                                console.log('aqui2');
                                let id_fuente = $(this).attr("name").split("_")[2];
                                let valor_fuente = $(this).val();
                                let fila = $(this).closest('tr');
                                let valorSelect = fila.find('.select_observacion').val();
                                console.log('valor observacion'+valorSelect);
                                fuentes.push({
                                    id_fuente: id_fuente,
                                    valor_fuente: valor_fuente,
                                    valorSelectObs: valorSelect
                                });
                            } else{
                                let id_condicion = this.name.split("_")[1]; 
                                let valor_condicion = $(this).val();
                                condiciones.push({
                                    id_condicion: id_condicion,
                                    valor_condicion: valor_condicion
                                });
                            }
                        });
                        console.log(fuentes);
                        $.ajax({
                            url: '/evaluacion/grabarcalculocriterio',
                            async: false,
                            type: 'POST',
                            contentType: "application/json",
                            data: JSON.stringify({
                                id_autoevaluacion: $('#id_autoevaluacion').val(),
                                id_criterio_calcular: $('#id_criterio_calcular').val(),
                                puntaje_total_criterio: $('#puntaje_total_criterio').val(),
                                fuentes_data: fuentes,
                                condiciones_data: condiciones,
                                filesToSend: $('#filesToSend').val()
                            }),
                            success: function (res) {
                                if (res.success) {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Criterio Calificado Exitosamente',
                                        text: res.message
                                    });
                                } else{
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error en Grabar Fuentes',
                                        text: res.message
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