let table;
function cargarTablaFuentes(idProceso) {


    table = $("#tablaFuentes").DataTable({
        destroy: true,
        pageLength: 40,
        ordering: false,
        columnDefs: [
            {
                targets: 4
            }
        ],
        ajax: {
            url: `/procesos/api/process/${idProceso}/fuentes`,
            dataSrc: "fuentes"
        },
        createdRow: function (row, data, dataIndex) {
            $(row).attr("data-id-fuente", data.id_fuente);
        },

        columns: [
            { data: "codigo_criterio" },
            {
                data: "nombre_condicion",
                render: (data) => data ? data : ""
            },
            { data: "nombre_fuente" },
            {
            data: null,
            render: function (row) {


                // --- Si existe link_fuente: mostrar solo texto ---
                if (row.link_fuente && row.link_fuente.trim() !== "") {
                return `
                    <div style="display:flex; gap:8px;" data-codigo-criterio="${row.codigo_criterio || ''}">
                    <input type="hidden" class="hiddenCodigoCriterio" value="${row.codigo_criterio || ''}">
                    <a href="${row.link_fuente}" target="_blank">${row.link_fuente}</a></div>`;
                }
                
                if (row.permiso == 'view')  {
                    if (row.link_reporte){

                        return  `link<input type="text"
                                    class="form-control inputLinkReporte"
                                    data-id="${row.id_fuente}"
                                    value="${row.link_reporte ?? ""}"
                                    placeholder="Pega aquí la URL"
                                    style="max-width:1000px; font-size:13px;">`;
                    }
                    else{
                        return ` <div style="position:relative; max-width:440px;">
                            <input type="text"
                                    class="form-control inputNombreArchivo"
                                    value="${row.nombre_archivo || "Sin archivo"}"
                                    readonly
                                    style="cursor:pointer; font-size:13px;">

                            ${
                                row.ruta_archivo
                                ? `<a href="/procesos/uploads/fuentes/${row.ruta_archivo}"
                                        target="_blank"
                                        style="position:absolute; top:0; left:0;
                                            width:100%; height:100%; z-index:5;"></a>`
                                : ""
                            }
                            </div>`;
                    }
                }
                else {
                    const tipo = row.link_reporte ? "link" : "archivo";
                    return `
                    <div style="display:flex; gap:8px;" class="archivo-wrapper"
                        data-tipo="${tipo}"
                        data-codigo-criterio="${row.codigo_criterio || ''}"
                        style="display:flex; flex-direction:column; gap:6px; max-width:3000px;">

                        <!-- HIDDEN CLAVE -->
                        <input type="hidden"
                            class="hiddenCodigoCriterio"
                            value="${row.codigo_criterio || ''}">

                        <!-- SELECT -->
                        <select class="form-select tipoArchivoSelect"
                                data-id="${row.id_fuente}"
                                style="max-width:100px; font-size:13px;">
                        <option value="link" ${row.link_reporte ? "selected" : ""}>Link</option>
                        <option value="archivo" ${row.link_reporte ? "" : "selected"}>Fuente</option>
                        </select>

                        <!-- BLOQUE LINK -->
                        <div class="bloque-link" style="display:${row.link_reporte ? "block" : "none"};">
                        <div style="display:flex; gap:10px;">
                            <input type="text"
                                class="form-control inputLinkReporte"
                                data-id="${row.id_fuente}"
                                value="${row.link_reporte ?? ""}"
                                placeholder="Pega aquí la URL"
                                style="max-width:1000px; font-size:13px;">
                            <button class="btn btn-success btnSaveLink" data-id="${row.id_fuente}">Guardar</button>
                        </div>
                        </div>

                        <!-- BLOQUE ARCHIVO -->
                        <div class="bloque-archivo" style="display:${row.link_reporte ? "none" : "block"};">
                        <div style="display:flex; gap:10px; align-items:center;">
                            <div style="position:relative; max-width:440px;">
                            <input type="text"
                                    class="form-control inputNombreArchivo"
                                    value="${row.nombre_archivo || "Sin archivo"}"
                                    readonly
                                    style="cursor:pointer; font-size:13px;">

                            ${
                                row.ruta_archivo
                                ? `<a href="/procesos/uploads/fuentes/${row.ruta_archivo}"
                                        target="_blank"
                                        style="position:absolute; top:0; left:0;
                                            width:100%; height:100%; z-index:5;"></a>`
                                : ""
                            }
                            </div>
                            <label class="btn btn-primary btn-sm mb-0">Subir
                            <input type="file" class="fileUpload d-none" accept=".pdf,.docx,.xlsx,.xls" data-id="${row.id_fuente}">
                            </label>
                            <button class="btn btn-success btn-sm btnSaveFile" data-id="${row.id_fuente}" ${!row.ruta_archivo ? 'disabled title="Primero sube un archivo con el botón Subir"' : ''}>Guardar</button>                    
                        </div>
                        </div>
                    </div>`;
                }
            }
            },
            {
                data: "es_observado",               
                render: function (data, type, row) {

                    let checkClass = "text-muted";
                    let xClass = "text-muted";

                    // ✔ VALIDADO
                    if ((data === 1) || (row.link_fuente!= "")){
                        checkClass = "text-success";
                    }

                    // ✖ OBSERVADO
                    if (data === 0) {
                        xClass = "text-danger";
                    }
                    return `
                        <div style="display:flex; gap:8px; align-items:center;">
                        <i class="fa fa-check-circle ${checkClass}"
                        style="font-size:26px; margin-right:8px;"></i>
                        <i class="fa fa-times-circle ${xClass}"
                        style="font-size:26px;"></i></div>
                    `;
                }
            },
            { data: "observacion_fuente" }
        ],

        language: { url: "/static/json/es-ES.json" }
    });


    // -------------------------------------------------------------
    // Evento: Mostrar nombre del archivo al seleccionar (subida temp)
    // -------------------------------------------------------------
    $(document).off("change", ".fileUpload").on("change", ".fileUpload", async function () {
        const file = this.files[0];
        const id_fuente = $(this).data("id");
        const inputNombre = $(this).closest("div").find(".inputNombreArchivo");
        const btnSave = $(this).closest("label").siblings(".btnSaveFile");
        const labelSubir = $(this).closest("label");

        if (!file) return;

        // Loading: deshabilitar y mostrar "Subiendo..."
        inputNombre.val("Subiendo...");
        labelSubir.addClass("disabled").css("pointer-events", "none");
        const wrapper = inputNombre.closest(".archivo-wrapper");
        let $spinner = wrapper.find(".upload-spinner");
        if (!$spinner.length) {
            $spinner = $(`<span class="upload-spinner ms-2"><span class="spinner-border spinner-border-sm text-primary" role="status"></span></span>`);
            inputNombre.after($spinner);
        }
        $spinner.show();

        try {
            let formData = new FormData();
            formData.append("file", file);

            const resp = await fetch(`/procesos/api/fuente/${id_fuente}/temp`, {
                method: "POST",
                body: formData
            });

            const data = await resp.json().catch(() => ({}));

            if (!resp.ok) {
                console.error("Error temp upload:", data);
                alert(data.error || "Error subiendo archivo temporal");
                btnSave.removeData("temp").removeData("real");
                inputNombre.val("Sin archivo");
                return;
            }
            btnSave.data("temp", data.nombre_temp);
            btnSave.data("real", data.nombre_archivo);
            inputNombre.val(data.nombre_archivo || file.name);
            btnSave.prop("disabled", false).attr("title", "Guardar archivo en el servidor");
            console.log("Temp upload OK for", id_fuente, data);
        } finally {
            labelSubir.removeClass("disabled").css("pointer-events", "");
            wrapper.find(".upload-spinner").hide();
        }
    });


    // -------------------------------------------------------------
    // Evento: Guardar archivo final (usa datos guardados en btn)
    // -------------------------------------------------------------
    $(document).off("click", ".btnSaveFile").on("click", ".btnSaveFile", async function () {

        const id_fuente = $(this).data("id");
        const btn = $(this);

        // buscar fila vía data-id-fuente (asegura unicidad)
        const fila = btn.closest(`tr[data-id-fuente="${id_fuente}"]`);
        if (!fila || fila.length === 0) {
            alert("No se encontró la fila correspondiente (id_fuente: " + id_fuente + ")");
            return;
        }

        // usar datos temporales guardados al seleccionar archivo
        const nombre_temp = btn.data("temp");
        const nombre_real = btn.data("real");

        if (!nombre_temp) {
            Swal.fire({
                icon: 'warning',
                title: 'Subir Documento',
                text: 'Primero selecciona un archivo con "Subir" y espera a que termine la subida. Luego pulsa "Guardar".',
                confirmButtonColor: '#3E97FF'
            });
            return;
        }

        // Limpiar datos del botón de inmediato para evitar doble envío (evita "Archivo temporal no existe")
        btn.removeData("temp").removeData("real");

        // Loading: deshabilitar botón y mostrar spinner
        const btnText = btn.text().trim();
        btn.prop("disabled", true).html('<span class="spinner-border spinner-border-sm me-1" role="status"></span> Guardando...');

        let saveData = {};
        try {
            const resp = await fetch(`/procesos/api/fuente/${id_fuente}/upload`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    nombre_temp,
                    nombre_real
                })
            });

            const contentType = resp.headers.get("content-type") || "";
            saveData = contentType.indexOf("application/json") !== -1
                ? await resp.json().catch(() => ({}))
                : { error: "Error en el servidor (respuesta no válida)" };

            if (!resp.ok) {
                console.error("Error saving final:", saveData);
                alert(saveData.error || "Error al guardar final");
                btn.prop("disabled", false).html(btnText);
                return;
            }
        } catch (err) {
            console.error("Error saving final:", err);
            alert("Error de conexión al guardar");
            btn.prop("disabled", false).html(btnText);
            return;
        }

        // === Actualizar SOLO la fila afectada ===
        // 1) actualizar el input visible
        fila.find(".inputNombreArchivo").val(saveData.nombre_archivo || nombre_real);

        // 2) actualizar o añadir overlay <a> para que el input sea clickeable
        // construir nuevo link si el servidor devolvió ruta_archivo
        const ruta = saveData.ruta_archivo || saveData.ruta || nombre_temp;
        if (ruta) {
            // si existe overlay, reemplazar href; si no, crear overlay
            let overlay = fila.find("a").filter(function () {
                // elegir overlay absoluto (posicionado)
                return $(this).css("position") === "absolute" || $(this).attr("target") === "_blank";
            }).first();

            const linkUrl = `/procesos/uploads/fuentes/${ruta}`;

            if (overlay && overlay.length) {
                overlay.attr("href", linkUrl);
            } else {
                // insertar overlay (posicionado sobre el input)
                const wrapper = fila.find("div").first(); // el wrapper con position:relative
                if (wrapper && wrapper.length) {
                    wrapper.append(`<a href="${linkUrl}" target="_blank"
                        style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:5;"></a>`);
                }
            }
        }

        // 3) restaurar texto del botón (datos ya se limpiaron al iniciar)
        btn.prop("disabled", false).html("Guardar");

        Swal.fire({
            icon: 'success',
            title: 'Archivo guardado',
            text: 'Archivo guardado exitosamente',
            confirmButtonColor: '#3E97FF'
        });
        table.ajax.reload(null, false);
    });
} // end cargarTablaFuentes

$(document).off("change", ".tipoArchivoSelect").on("change", ".tipoArchivoSelect", function () {
    const tipo = $(this).val();
    const wrapper = $(this).closest(".archivo-wrapper");
    wrapper.attr("data-tipo", tipo);
    // Mostrar/ocultar bloques
    wrapper.find(".bloque-link").toggle(tipo === "link");
    wrapper.find(".bloque-archivo").toggle(tipo === "archivo");
});


$(document).off("click", ".btnSaveLink").on("click", ".btnSaveLink", async function () {
    const id_fuente = $(this).data("id");
    // localizar fila correcta
    const fila = $(this).closest(`tr[data-id-fuente="${id_fuente}"]`);
    if (!fila || fila.length === 0) {
        Swal.fire({
            icon: 'error',
            title: 'Link incorrecto',
            text: 'Fila no encontrada',
            confirmButtonColor: '#3E97FF'
        });
        return;
    }

    // obtener el valor del input
    const inputLink = fila.find(".inputLinkReporte");
    const link = inputLink.val().trim();

    if (!link) {
        Swal.fire({
            icon: 'error',
            title: 'Link incorrecto',
            text: 'El link esta vacio',
            confirmButtonColor: '#3E97FF'
        });
        return;
    }

    if (!(link.startsWith("http://") || link.startsWith("https://"))) {
        Swal.fire({
            icon: 'error',
            title: 'Link incorrecto',
            text: 'El link debe comenzar con http:// o https://',
            confirmButtonColor: '#3E97FF'
        });
        return;
    }
    //Grabar link en bd
    const resp = await fetch(`/procesos/api/fuente/${id_fuente}/link`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ link })
    });

    const data = await resp.json();

    if (!resp.ok) {
        alert(data.error || "Error al guardar link");
        return;
    }

    Swal.fire({
        icon: 'success',
        title: 'Guardado correctamente',
        text: 'El enlace fue registrado exitosamente.',
        confirmButtonColor: '#3E97FF'
    });
    table.ajax.reload(null, false);
    // actualizar fila del datatable (solo interfaz)
    inputLink.val(link);
});

