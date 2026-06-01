var RedesEvent = {

    init: function () {
        this.loadTabla();
        this.loadDropdowns();    
        this.bindEvents();
    },
    loadTabla: function () {

        let tabla = $("#tablaRedes").DataTable({
            destroy: true,
            ajax: {
                url: "/redes/lista",
                dataSrc: ""
            },
            columns: [
                { data: "codigo_red" },
                { data: "nombre_red" },
                { data: "macrorregion" },
                {
                    data: null,
                    render: function (data, type, row) {
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-red" 
                        data-id="${row.id_red}" data-bs-toggle="modal" data-bs-target="#Modal_EditarRed" data-tipo="edit" >
                        <i class="fas fa-edit"></i> Editar </button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-red"
                        data-id="${row.id_red}" data-bs-toggle="modal" data-bs-target="#Modal_EditarRed" data-tipo="ver" >
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
        $.ajax({
            url: '/macrorregion/api/macrorregiones',
            type: 'GET',
            success: function (data) {
                const selectMacrorregion = $('#sel_macrorregion');
                selectMacrorregion.empty();               
                data.forEach(r => {
                    selectMacrorregion.append(new Option(r.nombre_macrorregion, r.id_macrorregion));
                });
                selectMacrorregion.select2({
                    placeholder: "Seleccione una macrorregión",
                    width: '100%'
                });
            },
            error: function () {
                console.error('Error al cargar macrorregiones');
            }
        });
    },
    bindEvents: function(){

        $('#Modal_EditarRed').on('hidden.bs.modal', function () {
            $('.btn-back-gris').trigger('focus');
        });

        $('body').on('click','.btn-edit-red', function () {
            let redId = $(this).data('id');
            let mode = $(this).data('tipo');
            $.ajax({
                url: `/redes/${redId}`,
                type: 'GET',
                success: function (data) {
                    $('#form_nueva_red').find('#nombre_red').val(data.nombre_red);
                    $('#form_nueva_red').find('#sel_macrorregion').val(data.macrorregion).trigger('change');
                },
                error: function () {
                    alert("Error al cargar los datos del usuario");
                }
            });
            if (mode === 'ver') {
                $('#Modal_EditarRed').find('input, select, textarea').prop('disabled', true);
                $('#Modal_EditarRed').find('.modal-footer').hide();
                $('#Modal_EditarRed').find('.modal-title').text('Ver Red');
            } else {
                $('#Modal_EditarRed').find('input, select, textarea').prop('disabled', false);
                $('#Modal_EditarRed').find('.modal-footer').show();
                $('#Modal_EditarRed').find('.modal-title').text('Editar Red');
            }
        });



    }
};
