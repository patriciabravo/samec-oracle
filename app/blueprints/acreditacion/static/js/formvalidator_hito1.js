var FormValidatorHito1 = {
    init: function () {
        this.formvalidatorHito1();
    },
    formvalidatorHito1: function () {
        const form = document.getElementById("form_hito_1");
        const submitButton = document.getElementById("btnGuardarComite");
        const validator = FormValidation.formValidation(form, {
            fields: {
                "nombre_comite": {
                    validators: {
                        notEmpty: {
                            message: "Ingrese el nombre del Participante"
                        }
                    }
                }
            },
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap5({
                    rowSelector: "td",
                    eleInvalidClass: "",
                    eleValidClass: ""
                }),
                submitButton: new FormValidation.plugins.SubmitButton()
            }
        })
        .on('core.form.valid', function () {
            console.log("llega aqui");
            $.ajax({
                url: '/acreditacion/api/hito-1/guardar',
                async: false,
                type: 'POST',
                data: $(form).serialize(),
                success: function (res) {
                    if (res.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Hito 1 Registrado',
                            text: res.message
                        }).then(() => {
                            $('#modalHito1').modal('hide');
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error al Registrar',
                            text: res.message
                        });
                    }
                },
                error: function (err) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: err.responseJSON?.message || 'Ocurrió un problema al registrar'
                    });
                }
            });
        });

    }
}