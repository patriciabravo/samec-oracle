var ListadoEvent = {

    contadorComite: 1,
    init: function () {
        this.events();
        this.generartemplates();
    },
    events: function () {
        let self = this;

        $(document).on('hidden.bs.modal', '#modalHito1', function () {
            document.activeElement?.blur();
        });

        $(document).on('click','.btn-edit-hito1', function () {
            let IdAcreditacion = $(this).data('id');
            console.log(IdAcreditacion);
            $.ajax({
                url: `/acreditacion/hito1/${IdAcreditacion}`,
                type: 'GET',
                success: function(response) {
                    if (!response.success) {
                        alert('No se pudo obtener la información');
                        return;
                    }
                    const miembros = response.data;
                    $('#tablaMiembros').find('tbody#filas_miembros').empty();
                    miembros.forEach(function(miembro) {
                        let fila = `
                            <tr>
                                <td><input type="hidden" name="id_miembro[]" value="${miembro.id_miembro}">
                                    <input type="text" class="form-control" name="miembro_nombre[]" value="${miembro.nombre_miembro}">
                                </td>
                                <td>
                                    <input type="text" class="form-control" name="miembro_cargo[]" value="${miembro.cargo_miembro}">
                                </td>
                                <td>
                                    <select class="form-select" name="miembro_lider[]">
                                        <option value="0" ${miembro.es_lider == 0 ? 'selected' : ''}>NO</option>
                                        <option value="1" ${miembro.es_lider == 1 ? 'selected' : ''}>SI</option>
                                    </select>
                                </td>
                                <td class="text-center">
                                    <button type="button" class="btn btn-light-danger btn-sm btnEliminarMiembro"><i class="bi bi-trash"></i></button>
                                </td>
                            </tr>`;
                        $('#tablaMiembros').find('tbody#filas_miembros').append(fila);
                    });
                    $('#modalHito1').modal('show');
                },
                error: function(xhr) {
                    console.error(xhr);
                    alert('Error al cargar la información');
                }
            });
        });

        $('#btnAgregarMiembro').on('click', function () {
            ListadoEvent.agregarFilaComite();
        });

        $(document).on('click', '.btnEliminarMiembro', function () {
            $(this).closest('tr').remove();
        });

        const previewTemplate = `<div class="dz-preview d-flex justify-content-between align-items-center border rounded p-2 mb-1">
            <i class="bi bi-file-earmark-pdf fs-2 text-primary"></i>&nbsp;<span class="text-primary pl-2" data-dz-name></span>&nbsp;
            <a class="btn btn-sm btn-light-danger" data-dz-remove><i class="bi bi-trash fs-2"></i></a>
            </div>`;
        $('.dropzone_hitos').each(function () {
            if (this.dropzone) {
                return;
            }
            const modal_name = $(this).closest('#modalResolucionHito1');
            new Dropzone(this, {
                url: '/auth/uploadhito',
                previewTemplate: previewTemplate,
                paramName: "file",
                maxFiles: 1,
                maxFilesize: 1,
                acceptedFiles: ".pdf",
                createImageThumbnails: false,
                dictDefaultMessage: "<i class='bi bi-cloud-upload fs-2 btn-text-azul'></i><br><span class='btn-text-azul'>Arrastre un PDF o haga clic aquí</span>",
                addRemoveLinks: true,
                    init: function () {
                            this.on("success", function (file, response) {
                                file.server_name = response.upload_filename;
                                file.isNew = true;
                                $('.filesToInsertDB').val(JSON.stringify([{
                                    real_filename: response.real_filename,
                                    upload_filename: response.upload_filename
                                }]));
                            });
                            this.on("removedfile", function (file) {
                                $('.filesToInsertDB').val("");
                                if (file.server_name && file.isNew) {
                                    $.ajax({
                                        url: `/auth/delete-evidencia/${file.server_name}`,
                                        type: "DELETE"
                                    });
                                }
                                if (this.files.length === 0) {
                                    modal_name.find('.btn-save-hito').show();
                                }
                            });
                            this.on("addedfile", function (file) {
                                file.previewElement.addEventListener("click", function (e) {
                                    if (e.target.classList.contains("dz-remove")) {
                                        return;
                                    }
                                    let url = "";
                                    if (file.server_name) {
                                        url = "/uploads/temp_fuentes/" + file.server_name;
                                    }
                                    if (url) {
                                        window.open(url, "_blank");
                                    }
                                });
                                modal_name.find('.btn-save-hito').show();
                            });

                        }
            });
        });

    },
    agregarFilaComite: function () {

        let fila = `
            <tr>
                <td>
                    <input type="text"
                           class="form-control"
                           name="miembro_nombre[]"
                           placeholder="Ingrese nombre">
                </td>
                <td>
                    <input type="text"
                           class="form-control"
                           name="miembro_cargo[]"
                           placeholder="Ingrese cargo">
                </td>
                <td>
                    <select class="form-select"
                            name="miembro_lider[]">
                        <option value="0" selected>NO</option>
                        <option value="1">SI</option>
                    </select>
                </td>
                <td class="text-center">
                    <button type="button"
                            class="btn btn-light-danger btn-sm btnEliminarComite">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        $('#tablaMiembros').find('tbody#filas_miembros').append(fila);
        this.contadorComite++;
    },
    generartemplates: function() {

        $('#btnDescargarHito1').on('click', function (e) {
            e.preventDefault();
            console.log('el boton descargar');
            let id_autoevaluacion = $('#id_autoevaluacion').val();
            window.open(`/acreditacion/api/hito-1/word/${id_autoevaluacion}`,'_blank');
        });

    }   


};
