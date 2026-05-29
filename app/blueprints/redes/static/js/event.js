var RedesEvent = {

    init: function () {
        this.loadTabla();
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
                        btn_edit= `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-persona" 
                        data-id="${row.id_red}" data-bs-toggle="modal" data-bs-target="#CrearRed" data-tipo="edit" >
                        <i class="fas fa-edit"></i> Editar </button>`;
                        btn_view=  `<button class="btn btn-sm btn-secondary me-3 btn-text-azul btn-edit-persona"
                        data-id="${row.id_red}" data-bs-toggle="modal" data-bs-target="#CrearRed" data-tipo="ver" >
                        <i class="fas fa-eye"></i> Ver </button>`;                           
                        return  btn_edit + btn_view;
                    }
                    
                }
            ],
            language: {
                url: "/static/json/es-ES.json"
            }
        });
    }
};
