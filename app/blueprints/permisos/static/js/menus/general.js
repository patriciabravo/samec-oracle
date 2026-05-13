var MenuEvent = {

    init: function() {
        console.log('Inicializando DataTable de menús');
        this.loadMenus();
    },

    loadMenus: function() {
         $('#tablaMenus').DataTable({
            ajax: {
                url: 'permisos/api/menus',
                dataSrc: ''
            },
            columns: [
                { data: 'id_menu' },
                { data: 'nombre_menu' },
                { 
                    data: 'icono_menu',
                    render: function(data, type, row) {
                        return `<img src="/static/media/icons/menu_icons/${data}" width="32" height="32" alt="icono">`;
                    }
                }
            ],

            language: {
                url: 'https://cdn.datatables.net/plug-ins/2.1.3/i18n/es-ES.json'
            }
        });
    }
};
