var OptionEvent = {

    init: function() {
        console.log('Inicializando DataTable de Opciones');
        this.loadOpciones();
        this.loadMenus();

    },

    loadOpciones: function() {
        const tabla = $('#tablaOpciones').DataTable({
            ajax: {
                url: '/permisos/api/opciones/0',
                dataSrc: ''
            },
            columns: [
                { data: 'id_opcion' },
                { data: 'nombre_opcion' },
                { data: 'ruta_opcion' },
                { data: 'nombre_menu' },
                { 
                    data: 'activo_texto',
                    render: function(data, type, row) {
                        return row.activo
                            ? '<i class="fa fa-check-circle text-success"></i> Activo'
                            : '<i class="fa fa-times-circle text-danger"></i> Inactivo';
                    }
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    render: function(data, type, row) {
                        return `
                            <button class="btn btn-sm btn-secondary me-2 btn-ver-opcion"
                                data-id="${row.id_opcion}" data-mode="ver" data-bs-toggle="modal" data-bs-target="#modalEditarOpcion">
                                <i class="fas fa-eye"></i> Ver
                            </button>
                            <button class="btn btn-sm btn-secondary me-2 btn-editar-opcion"
                                data-id="${row.id_opcion}" data-mode="editar" data-bs-toggle="modal" data-bs-target="#modalEditarOpcion">
                                <i class="fas fa-edit"></i> Editar
                            </button>
                        `;
                    }
                }
            ],
            language: {
                url: "/static/json/es-ES.json"
            }
        });

        // --- Evento click para Ver o Editar ---
        $('body').on('click', '.btn-ver-opcion, .btn-editar-opcion', function() {
            let opcionId = $(this).data('id');
            let mode = $(this).data('mode'); // "ver" o "editar"

            $.ajax({
                url: `permisos/api/opciones/${opcionId}`,
                type: 'GET',
                success: function (data) {
                    const opcion = data[0];
                    $('#id_opcion').val(opcion.id_opcion);
                    $('#nombre_opcion').val(opcion.nombre_opcion);
                    $('#ruta_opcion').val(opcion.ruta_opcion);
                    $('#id_menu').val(opcion.id_menu);
                    $('#nombre_menu').val(opcion.nombre_menu);
                    $('#activo').val(opcion.activo ? 'true' : 'false');

                    // --- Configurar modo (ver / editar) ---
                    if (mode === 'ver') {
                        $('#modalEditarOpcion').find('input, select, textarea').prop('disabled', true);
                        $('#modalEditarOpcion').find('.modal-footer').hide();
                        $('#modalEditarOpcion').find('.modal-title').text('Ver opción');
                    } else {
                        $('#modalEditarOpcion').find('input, select, textarea').prop('disabled', false);
                        $('#modalEditarOpcion').find('.modal-footer').show();
                        $('#modalEditarOpcion').find('.modal-title').text('Editar opción');
                    }
                },
                error: function(xhr) {
                    Swal.fire('Error', 'No se pudieron cargar los datos de la opción', 'error');
                    console.error(xhr.responseText);
                }
            });
        });
        // --- Crear nueva opción ---
$('#form_nueva_opcion').on('submit', function(e) {
    e.preventDefault();
    const form = $(this);

    $.ajax({
        url: form.attr('action'),
        type: 'POST',
        data: form.serialize(),
        success: function(response) {
            if (response.success) {
                $('#modalNuevaOpcion').modal('hide');
                $('#tablaOpciones').DataTable().ajax.reload();
                Swal.fire({
                    icon: 'success',
                    title: 'Opción creada',
                    text: response.message,
                    timer: 1500,
                    showConfirmButton: false
                });
                form.trigger('reset');
            } else {
                Swal.fire('Error', response.message, 'error');
            }
        },
        error: function(xhr) {
            Swal.fire('Error', 'No se pudo crear la opción', 'error');
            console.error(xhr.responseText);
        }
    });
    
});




        // --- Guardar cambios ---
        $('#form_editar_opcion').on('submit', function(e) {
            e.preventDefault();
            const form = $(this);

            $.ajax({
                url: form.attr('action'),
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    if (response.success) {
                        $('#modalEditarOpcion').modal('hide');
                        $('#tablaOpciones').DataTable().ajax.reload();
                        tabla.ajax.reload();
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: response.message,
                            timer: 1500,
                            showConfirmButton: false
                        });
                    } else {
                        Swal.fire('Error', response.message, 'error');
                    }
                },
                error: function(xhr) {
                    Swal.fire('Error', 'Ocurrió un problema al actualizar la opción', 'error');
                    console.error(xhr.responseText);
                }
            });
        });
    },
    loadMenus: function() {
    $.ajax({
        url: '/permisos/api/menus',
        type: 'GET',
        success: function(data) {
            let select = $('#nuevo_id_menu');
            select.empty();
            select.append(`<option value="">Seleccione...</option>`);

            data.forEach(row => {
                select.append(`<option value="${row.id_menu}">
                                ${row.nombre_menu}
                               </option>`);
            });
        }
    });

},


}
