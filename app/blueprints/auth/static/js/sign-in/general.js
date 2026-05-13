"use strict";
var KTSigninGeneral = function () {
    var t,
        e,
        r,
        errorDiv;
    return {
        init: function () {
            t = document.querySelector("#kt_sign_in_form"),
            e = document.querySelector("#kt_sign_in_submit"),
            errorDiv = document.querySelector("#login-error"),
            r = FormValidation.formValidation(t, {
                fields: {
                    usuario: {
                        validators: {
                            regexp: {
                                regexp: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                message: "No es un usuario válido"
                            },
                            notEmpty: {
                                message: "Se requiere el usuario"
                            }
                        }
                    },
                    password: {
                        validators: {
                            notEmpty: {
                                message: "Se requiere la contraseña"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            }),

            !function (t) {
                try {
                    return new URL(t), !0
                } catch (t) {
                    return !1
                }
            }(e.closest("form").getAttribute("action")) 

            ? e.addEventListener("click", function (i) {
                i.preventDefault();
                errorDiv.textContent = "";
                const $form = $("#kt_sign_in_form"); 
                $.ajax({
                    url: $form.attr("action"),
                    type: "POST",
                    data: $form.serialize(), 
                    success: function(response) {
                        if (response.success) {
                            window.location.href = response.redirect_url;
                        } else {
                            errorDiv.textContent = response.message;
                        }
                    },
                    error: function(xhr) {
                        let msg = "Error de conexión. Intente nuevamente.";
                        if (xhr.responseJSON && xhr.responseJSON.message) {
                            msg = xhr.responseJSON.message;
                        }
                        errorDiv.textContent = msg;
                    }
                });
            })

            : e.addEventListener("click", function (i) {
                i.preventDefault();
            });

            // ----------------------------------------------------------
            // 🚀 PERMITIR INICIAR SESIÓN CON LA TECLA ENTER
            // ----------------------------------------------------------
            t.addEventListener("keypress", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    e.click(); // Simula el clic del botón
                }
            });
            // ----------------------------------------------------------
        }
    }
}();

KTUtil.onDOMContentLoaded(function () {
    KTSigninGeneral.init();
});
