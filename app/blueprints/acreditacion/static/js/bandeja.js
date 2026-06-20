var ListadoEvent = {

    contadorComite: 1,
    init: function () {
        this.events();
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
    events: function () {
        let self = this;
        $('#btnAgregarMiembro').on('click', function () {
            ListadoEvent.agregarFilaComite();
        });

        $(document).on('click', '.btnEliminarComite', function () {
            $(this).closest('tr').remove();
        });

        $(document).on('hidden.bs.modal', '#modalHito1', function () {
            document.activeElement?.blur();
        });

        $('#btnDescargarHito1').on('click', function () {
            let id_autoevaluacion = $('#id_autoevaluacion').val();
            window.open(`/acreditacion/api/hito-1/word/3`,'_blank');
        });

        const previewTemplate = `<div class="dz-preview d-flex justify-content-between align-items-center border rounded p-2 mb-1">
            <i class="bi bi-file-earmark-pdf fs-2 text-primary"></i>&nbsp;<span class="text-primary pl-2" data-dz-name></span>&nbsp;
            <a class="btn btn-sm btn-light-danger" data-dz-remove><i class="bi bi-trash fs-2"></i></a>
            </div>`;
        $('.dropzone_hitos').each(function () {
            if (this.dropzone) {
                return;
            }
            const fila = $(this).closest('tr');
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
                                    fila.find('.btn-save-hito').show();
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
                                fila.find('.btn-save-hito').show();
                            });

                        }
            });
        });

    },
    agregarFilaComite: function () {
        let index = this.contadorComite;
        let fila = `
            <tr>
                <td>
                    <input type="text"
                           class="form-control"
                           name="miembro_nombre[${index}]"
                           placeholder="Ingrese nombre">
                </td>
                <td>
                    <input type="text"
                           class="form-control"
                           name="miembro_cargo[${index}]"
                           placeholder="Ingrese cargo">
                </td>
                <td>
                    <select class="form-select"
                            name="miembro_lider[${index}]">
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
        $('#tablaMiembros').append(fila);
        this.contadorComite++;
    }

};
