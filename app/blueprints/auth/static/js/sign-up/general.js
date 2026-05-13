"use strict";
var KTSignupGeneral = function () {
    var e,
    t,
    r,
    a,
    errorDiv,
    s = function () {
        return a.getScore() > 50
    };
    
    return {
        init: function () {
            e = document.querySelector("#kt_sign_up_form"),
            t = document.querySelector("#kt_sign_up_submit"),
            errorDiv = document.querySelector("#register-error"),
            a = KTPasswordMeter.getInstance(e.querySelector('[data-kt-password-meter="true"]')),
            !function (e) {
                try {
                    return new URL(e),
                    !0
                } catch (e) {
                    return !1
                }
            }            
                    (r = FormValidation.formValidation(e, {
                        fields: {
                            "nro_documento": {
                                validators: {
                                    notEmpty: {
                                        message: "Número es requerido"
                                    }
                                }
                            },
                            "first-name": {
                                validators: {
                                    notEmpty: {
                                        message: "Los nombres son requeridos"
                                    }
                                }
                            },
                            "last-name": {
                                validators: {
                                    notEmpty: {
                                        message: "Los Apellidos son requeridos"
                                    }
                                }
                            },
                            "redes": {
                                validators: {
                                    notEmpty: {
                                        message: "Redes es requerido"
                                    }
                                }
                            },
                            "ipress": {
                                validators: {
                                    notEmpty: {
                                        message: "Redes es requerido"
                                    }
                                }
                            },
                            email: {
                                validators: {
                                    regexp: {
                                        regexp: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                        message: "El valor no es una dirección de correo electrónico válida."
                                    },
                                    notEmpty: {
                                        message: "Correo electrónico requerido."
                                    }
                                }
                            },
                            password: {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la contraseña."
                                    },
                                    callback: {
                                        message: "Por favor, ingrese una contraseña válida.",
                                        callback: function (e) {
                                            if (e.value.length > 0)
                                                return s()
                                        }
                                    }
                                }
                            },
                            "confirm-password": {
                                validators: {
                                    notEmpty: {
                                        message: "Se requiere la confirmación de la contraseña."
                                    },
                                    identical: {
                                        compare: function () {
                                            return e.querySelector('[name="password"]').value
                                        },
                                        message: "La contraseña y su confirmación no coinciden."
                                    }
                                }
                            },
                            toc: {
                                validators: {
                                    notEmpty: {
                                        message: "Debe aceptar los términos y condiciones."
                                    }
                                }
                            }
                        },
                        plugins: {
                            trigger: new FormValidation.plugins.Trigger({
                                event: {
                                    password: !1
                                }
                            }),
                            bootstrap: new FormValidation.plugins.Bootstrap5({
                                rowSelector: ".fv-row",
                                eleInvalidClass: "",
                                eleValidClass: ""
                            })
                        }
                    }),
                    t.addEventListener("click", (function (s) {
                        s.preventDefault();
                        errorDiv.textContent = "";
                        const $form = $("#kt_sign_up_form"); 
                        $.ajax({
                            url: $form.attr("action"),
                            type: "POST",
                            data: $form.serialize(),
                            success: function(response) {
                                if (response.success) {
                                    Swal.fire({
                                                text: "Su usuario ha sido creado con éxito.",
                                                icon: "success",
                                                buttonsStyling: !1,
                                                confirmButtonText: "De acuerdo",
                                                customClass: {
                                                    confirmButton: "btn btn-primary"
                                                }
                                            }).then((result) => {
                                                if (result.isConfirmed) {
                                                    window.location.href = response.redirect_url || "/auth/register";
                                                }
                                            });
                                    
                                } else {
                                    errorDiv.textContent = response.message;
                                }
                            },
                            error: function(xhr) {
                                console.log("Error completo:", xhr);
                                let msg = "Error en el servidor. Intente nuevamente.";
                                if (xhr.responseJSON && xhr.responseJSON.message) {
                                    msg = xhr.responseJSON.message;
                                }
                                errorDiv.textContent = msg;
                            }
                        });
                        /*r.revalidateField("password"),
                        r.validate().then((function (r) {
                                "Valid" == r ? (t.setAttribute("data-kt-indicator", "on"), t.disabled = !0, setTimeout((function () {
                                            t.removeAttribute("data-kt-indicator"),
                                            console.log("data");
                                            t.disabled = !1,
                                            Swal.fire({
                                                text: "Su usuario ha sido creado con éxito.",
                                                icon: "success",
                                                buttonsStyling: !1,
                                                confirmButtonText: "De acuerdo",
                                                customClass: {
                                                    confirmButton: "btn btn-primary"
                                                }
                                            }).then((function (t) {                                                    
                                                    if (t.isConfirmed) {
                                                        e.reset(),
                                                        a.reset();
                                                        var r = e.getAttribute("data-kt-redirect-url");
                                                        r && (location.href = r)
                                                       e.submit();
                                                    }
                                                }))
                                        }), 1500)) : Swal.fire({
                                    text: "Lo sentimos, parece que se detectaron algunos errores. Por favor, inténtelo de nuevo.",
                                    icon: "error",
                                    buttonsStyling: !1,
                                    confirmButtonText: "Ok, entendido!",
                                    customClass: {
                                        confirmButton: "btn btn-primary"
                                    }
                                })
                            }))*/
                    })), 
                    e.querySelector('input[name="password"]').addEventListener("input", (function () {
                        this.value.length > 0 && r.updateFieldStatus("password", "NotValidated")
                    })))
                    

        }
    }
}
();
KTUtil.onDOMContentLoaded((function () {
        KTSignupGeneral.init()
    }));