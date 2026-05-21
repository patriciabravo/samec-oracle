var AutoevaluacionEvent = {
    init: function () {
        this.loadTabla();
    },
    loadTabla: function () {

        $('#btn_iniciar_autoevaluacion').on('click', async function(){
            let data = tabla.rows().data().toArray();
            for(let i=0;i<data.length;i++){
                let id_ipress = data[i].id_ipress;
                let es_activo = data[i].es_activo; 
                try{
                    if (es_activo){
                        await $.ajax({
                            url:`/autoevaluacion/api/autoevaluacionpuntajeautomatico/${id_ipress}`,
                            type:"GET"
                        });
                    }
                }catch(err){
                    console.error("Error con ipress:",id_ipress);
                }
            }
            tabla.ajax.reload();
        });

        let tabla = $('#tabla_ipress').DataTable({
            ajax:{
                url:"/autoevaluacion/api/ipress-autoevaluacion",
                dataSrc:""
            },
            columns:[
                {data:"id_ipress"},
                {data:"nombre"},
                {data:"nivel_ipress"},
                {data:"es_activo",
                   render: function(data, type, row){
                       if (data === null || data === "" || data === undefined  || data === 0) {
                            return '<span class="badge bg-danger text-white">Inactivo</span>';
                        } 
                        if (data == 1) {
                            return '<span class="badge bg-success text-white">Activo</span>';
                        }
                    }
                },
                {
                    data: "id_autoevaluacion",
                    render: function(data, type, row){
                        return data ? data : 'No Existe';
                    }
                },
                {
                    data: "estado",
                    render: function (data, type, row) {
                        if (data === null || data === "" || data === undefined) {
                            return '<span class="badge bg-secondary text-white">Sin iniciar</span>';
                        }
                        if (data == 1) {
                            return '<span class="badge bg-success text-white">AE - En Reporte</span>';
                        }
                        if (data == 2) {
                            return '<span class="badge bg-danger text-white">AE - En revision</span>';
                        }
                        return data;
                    }
                }
            ]

        });

    }
};


