from entidades import Cliente
from excepciones import ErrorSoftwareFJ
from gestor import SistemaGestionFJ
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def ejecutar_simulacion() -> None:
    sistema = SistemaGestionFJ()
    operaciones_ejecutadas = 0

    def correr_paso(numero: int, descripcion: str, accion, post_exito=None) -> None:
        nonlocal operaciones_ejecutadas
        operaciones_ejecutadas += 1
        print(f"\n--- Operación {numero}: {descripcion} ---")
        try:
            resultado = accion()
        except ErrorSoftwareFJ as exc:
            sistema.logger.error(
                f"Op {numero} fallida ({type(exc).__name__}): {exc} | Causa: {exc.__cause__}"
            )
        else:
            sistema.logger.info(f"Op {numero} exitosa -> {resultado}")
            if post_exito:
                post_exito(resultado)
        finally:
            print(f"Fin de operación {numero} (control de flujo estable).")

    # 1. Registro válido de cliente
    correr_paso(
        1,
        "Registro válido de cliente",
        lambda: sistema.registrar_cliente(Cliente("C-01", "Laura Gómez", "laura@empresa.com", "3105551234")) or "C-01 registrada",
    )

    # 2. Registro inválido de cliente (correo mal formado)
    correr_paso(
        2,
        "Registro inválido de cliente",
        lambda: sistema.registrar_cliente(Cliente("C-02", "Carlos Ruiz", "correo-no-valido", "3001112233")),
    )

    # 3. Creación válida de ReservaSala
    correr_paso(
        3,
        "Creación de servicio ReservaSala",
        lambda: sistema.registrar_servicio(ReservaSala("S-01", "Sala Ejecutiva A", 80000, capacidad=12)) or "S-01 creada",
    )

    # 4. Creación válida de AlquilerEquipo
    correr_paso(
        4,
        "Creación de servicio AlquilerEquipo",
        lambda: sistema.registrar_servicio(AlquilerEquipo("S-02", "Proyector 4K", 35000, stock_unidades=5)) or "S-02 creada",
    )

    # 5. Creación válida de AsesoriaEspecializada
    correr_paso(
        5,
        "Creación de servicio AsesoriaEspecializada",
        lambda: sistema.registrar_servicio(
            AsesoriaEspecializada("S-03", "Arquitectura Cloud", 120000, especialidad="AWS y Microservicios")
        )
        or "S-03 creada",
    )

    # 6. Creación inválida de servicio (tarifa negativa)
    correr_paso(
        6,
        "Creación inválida de servicio",
        lambda: sistema.registrar_servicio(ReservaSala("S-04", "Sala Beta", -50000, capacidad=6)),
    )

    # 7. Cálculo de costos (variantes y encadenamiento de excepción)
    correr_paso(
        7,
        "Cálculo de costos con descuento/IVA y prorrateo inválido",
        lambda: {
            "base_2h": sistema.buscar_servicio("S-01").calcular_costo(2),
            "con_desc_iva": sistema.buscar_servicio("S-01").calcular_costo(2, descuento_pct=10, impuesto_pct=19, asistentes=8),
            "prorrateo_error": sistema.calcular_con_encadenamiento("S-01", 2, 0),
        },
    )

    # 8. Reserva exitosa
    correr_paso(
        8,
        "Reserva exitosa de sala",
        lambda: sistema.crear_reserva("R-01", "C-01", "S-01", duracion_o_cantidad=3, asistentes=6),
    )

    # 9. Reserva fallida (cliente inexistente)
    correr_paso(
        9,
        "Reserva fallida por cliente inexistente",
        lambda: sistema.crear_reserva("R-02", "C-99", "S-02", duracion_o_cantidad=2, unidades=1),
    )

    # 10. Cancelación válida y luego reintento de cancelar la misma reserva (operación no permitida)
    def reintento_cancelacion(_):
        try:
            sistema.cancelar_reserva("R-01")
        except ErrorSoftwareFJ as exc:
            sistema.logger.error(
                f"Reintento en Op 10 fallido ({type(exc).__name__}): {exc}"
            )

    correr_paso(
        10,
        "Cancelación de R-01 y reintento inválido",
        lambda: sistema.cancelar_reserva("R-01") or "R-01 cancelada",
        post_exito=reintento_cancelacion,
    )

    print(f"\nSimulación completada: {operaciones_ejecutadas} operaciones ejecutadas sin interrupciones.")


if __name__ == "__main__":
    ejecutar_simulacion()