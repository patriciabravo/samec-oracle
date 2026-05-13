var RegisterEvent = {

    init: function() {

        $('#tipo_doc').select2({
					placeholder: "Tipo de documento",
					ajax: {
						url: URL_GET_TIPO_DOCUMENTO,
						dataType: 'json',
						delay: 250,
						processResults: function (data) {
							return {
								results: data.map(function(item) {
									return { id: item.id, text: item.nombre };
								})
							};
						},
						cache: true
					}
				});
		$('#redes').select2({
					placeholder: "Seleccione RED",
					ajax: {
						url: URL_GET_REDES,
						dataType: 'json',
						delay: 250,
						processResults: function (data) {
							return {
								results: data.map(function(item) {
									return { id: item.id, text: item.nombre };
								})
							};
						},
						cache: true
					}
				});

		$('#redes').on('change', function (e) {
				let redId = $(this).val();  // el ID de la ipress seleccionada
                let url_ipress = URL_GET_IPRESS.replace("0", redId);
				$('#ipress').val(null).trigger('change');				
				if (redId) {
					$('#ipress').select2({
						placeholder: "Seleccione IPRESS",
						ajax: {
							url: url_ipress,
							dataType: 'json',
							delay: 250,
							processResults: function (data) {
								return {
									results: data.map(function(item) {
										return { id: item.id, text: item.nombre };
									})
								};
							},
							cache: true
						}
					});
				} else {
					console.log("No se seleccionó ninguna IPRESS");
				}
		});

			
		Dropzone.autoDiscover = false;
        var dropzoneParams = {
            id: '#myDropzone',
            inputToInsertDB: '#filesToInsertDB',
            inputToDeleteDB: '#filesToDeleteDB',
            dirUploads: '/uploads',
            urlUploadProcessing: 'auth/uploadregistro',
        };
		/* en el preview template no se pone el dz-image */
        var myDropzoneAutorizacion = new Dropzone(dropzoneParams.id, {
            url: dropzoneParams.urlUploadProcessing,
            parallelUploads: 1,
            maxFiles: 1,
            maxFilesize: 2,
			dictFileTooBig: "El archivo es demasiado grande ({{filesize}}MB). Máx: {{maxFilesize}}MB.",
			dictDefaultMessage: "Seleccione el archivo de autorización",
			addRemoveLinks: true,
			acceptedFiles: ".pdf",
			init: function() {
				this.on("removedfile", function(file) {
					if (file.server_name) {
						$.ajax({
							url: `/auth/delete-file/${file.server_name}`,
							type: "DELETE",
							success: function(data) {
								console.log("Archivo eliminado:", data);
								$(dropzoneParams.inputToInsertDB).val("");
							},
							error: function(xhr, status, error) {
								console.error("Error al borrar:", error);
							}
						});
					}					
				});
				this.on("success", function(file, response) {
					if (response) {
						file.real_name = response.real_filename;
						file.server_name = response.upload_filename;
						var jsonString = JSON.stringify(response);
						$(dropzoneParams.inputToInsertDB).val(jsonString);
						console.log($(dropzoneParams.inputToInsertDB).val());
					}
				});
				this.on("maxfilesexceeded", function(file) {
					this.removeAllFiles();
					this.addFile(file);
				});
				this.on('addedfile', function(file) {
					var removeLink = file.previewElement.querySelector('[data-dz-remove]');
					console.log(removeLink);
					if (removeLink) {
					removeLink.innerHTML = '\
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">\
						<path fill="currentColor" d="M9 3h6l1 1h5v2H2V4h5l1-1zm1 6v9h2V9H10zm4 0v9h2V9h-2zM7 6h10v13a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V6z"/>\
						</svg>';
					removeLink.setAttribute('title', 'Eliminar archivo');
					removeLink.setAttribute('aria-label', 'Eliminar archivo');
					removeLink.classList.add('dz-remove-svg'); // opcional para estilos extra
					}
				});

			}
        });

    }
};