from datetime import datetime
import pytz  # Add this import
import logging

logger = logging.getLogger("model_file")


class ModelFile:
    @classmethod
    def get_all_by_id(cls, db_manager, id_carpeta, user):
        try:
            if id_carpeta != "0":
                sql = """
                    SELECT * FROM archivos 
                    WHERE id_usuario = %s AND id_carpeta = %s 
                    ORDER BY fecha_modificacion DESC
                """
                params = (user.id, id_carpeta)
            else:
                sql = """
                    SELECT * FROM archivos 
                    WHERE id_usuario = %s AND id_carpeta IS NULL 
                    ORDER BY fecha_modificacion DESC
                """
                params = (user.id,)

            results = db_manager.execute_query(sql, params)
            return results if results else []

        except Exception as e:
            logger.error(f"Error al obtener archivos: {e}")
            raise Exception(f"Error al obtener archivos: {e}")

    @classmethod
    def get_by_id(cls, db_manager, archivo_id, user):
        try:
            sql = """
                SELECT nombre_archivo FROM archivos 
                WHERE archivo_id = %s AND id_usuario = %s
            """
            result = db_manager.execute_query(sql, (archivo_id, user.id))

            return result[0]["nombre_archivo"] if result else None

        except Exception as e:
            logger.error(f"Error al obtener archivo por ID: {e}")
            raise Exception(f"Error al obtener archivo: {e}")

    @classmethod
    def delete_by_id(cls, db_manager, elemento_id, tabla, user):
        try:
            if tabla == "archivos":
                sql = """
                    SELECT id_archivo FROM archivos 
                    WHERE archivo_id = %s AND id_usuario = %s
                """
                result = db_manager.execute_query(sql, (elemento_id, user.id))
                id_archivos = result[0]["id_archivo"].split(",") if result else []

                sql = """
                    DELETE FROM archivos 
                    WHERE archivo_id = %s AND id_usuario = %s
                """
                db_manager.execute_query(sql, (elemento_id, user.id))

                return id_archivos

            elif tabla == "carpetas":
                archivos_a_eliminar = []

                # Función recursiva para obtener archivos de las subcarpetas
                def obtener_archivos_subcarpetas(carpeta_id):
                    sql_archivos = """
                        SELECT id_archivo FROM archivos 
                        WHERE id_carpeta = %s AND id_usuario = %s
                    """
                    result = db_manager.execute_query(
                        sql_archivos, (carpeta_id, user.id)
                    )
                    if result:
                        archivos_a_eliminar.extend(
                            [row["id_archivo"] for row in result]
                        )

                    # Buscar subcarpetas
                    sql_subcarpetas = """
                        SELECT carpeta_id FROM carpetas 
                        WHERE id_carpeta_padre = %s AND id_usuario = %s
                    """
                    result = db_manager.execute_query(
                        sql_subcarpetas, (carpeta_id, user.id)
                    )
                    subcarpetas = [row["carpeta_id"] for row in result]
                    for subcarpeta in subcarpetas:
                        obtener_archivos_subcarpetas(subcarpeta)

                obtener_archivos_subcarpetas(elemento_id)

                # Eliminar la carpeta
                sql = """
                    DELETE FROM carpetas 
                    WHERE carpeta_id = %s AND id_usuario = %s
                """
                db_manager.execute_query(sql, (elemento_id, user.id))

                # Eliminar los archivos asociados si hay archivos que eliminar
                if archivos_a_eliminar:
                    placeholders = ", ".join(["%s"] * len(archivos_a_eliminar))
                    sql = f"""
                        DELETE FROM archivos 
                        WHERE id_carpeta IN ({placeholders}) AND id_usuario = %s
                    """
                    params = archivos_a_eliminar + [user.id]
                    db_manager.execute_query(sql, params)

                return archivos_a_eliminar

        except Exception as e:
            logger.error(f"Error al eliminar elemento: {e}")
            raise Exception(f"Error al eliminar elemento: {e}")

    @classmethod
    def rename_by_id(cls, db_manager, archivo_id, nuevo_nombre, tabla, user):
        try:
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            if tabla == "archivos":
                extension_archivo = f".{nuevo_nombre.split('.')[-1]}"
                sql = """
                    UPDATE archivos 
                    SET nombre_archivo = %s, extension_archivo = %s, fecha_modificacion = %s 
                    WHERE archivo_id = %s AND id_usuario = %s
                """
                params = (
                    nuevo_nombre,
                    extension_archivo,
                    fecha_actual,
                    archivo_id,
                    user.id,
                )
            elif tabla == "carpetas":
                sql = """
                    UPDATE carpetas 
                    SET nombre_carpeta = %s, fecha_creacion = %s 
                    WHERE carpeta_id = %s AND id_usuario = %s
                """
                params = (nuevo_nombre, fecha_actual, archivo_id, user.id)

            db_manager.execute_query(sql, params)
            return True

        except Exception as e:
            logger.error(f"Error al renombrar: {e}")
            raise Exception(f"Error al renombrar: {e}")

    @classmethod
    def get_folders(cls, db_manager, id_carpeta_padre, user):
        try:
            if id_carpeta_padre != "0":
                sql = """
                    SELECT nombre_carpeta, color_carpeta, carpeta_id, fecha_creacion 
                    FROM carpetas 
                    WHERE id_carpeta_padre = %s AND id_usuario = %s 
                    ORDER BY nombre_carpeta ASC
                """
                params = (id_carpeta_padre, user.id)
            else:
                sql = """
                    SELECT nombre_carpeta, color_carpeta, carpeta_id, fecha_creacion 
                    FROM carpetas 
                    WHERE id_carpeta_padre IS NULL AND id_usuario = %s 
                    ORDER BY nombre_carpeta ASC
                """
                params = (user.id,)

            result = db_manager.execute_query(sql, params)
            return result if result else []

        except Exception as e:
            logger.error(f"Error al obtener carpetas: {e}")
            raise Exception(f"Error al obtener carpetas: {e}")

    @classmethod
    def create_folder(cls, db_manager, nombre_carpeta, id_carpeta_padre, user):
        try:
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            if id_carpeta_padre != "0":
                sql = """
                    INSERT INTO carpetas (id_usuario, nombre_carpeta, color_carpeta, id_carpeta_padre, fecha_creacion) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = (
                    user.id,
                    nombre_carpeta,
                    "c-2",
                    id_carpeta_padre,
                    fecha_actual,
                )
            else:
                sql = """
                    INSERT INTO carpetas (id_usuario, nombre_carpeta, color_carpeta, id_carpeta_padre, fecha_creacion) 
                    VALUES (%s, %s, %s, NULL, %s)
                """
                params = (user.id, nombre_carpeta, "c-2", fecha_actual)

            rows_affected = db_manager.execute_query(sql, params)
            return rows_affected > 0

        except Exception as e:
            logger.error(f"Error al crear carpeta: {e}")
            raise Exception(f"Error al crear carpeta: {e}")

    @classmethod
    def change_color_folder(cls, db_manager, color_carpeta, id_carpeta, user):
        try:
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            sql = """
                UPDATE carpetas 
                SET color_carpeta = %s, fecha_creacion = %s 
                WHERE carpeta_id = %s AND id_usuario = %s
            """
            db_manager.execute_query(
                sql, (color_carpeta, fecha_actual, id_carpeta, user.id)
            )
            return True

        except Exception as e:
            logger.error(f"Error al cambiar color de carpeta: {e}")
            raise Exception(f"Error al cambiar color de carpeta: {e}")

    @classmethod
    def get_parent_folder(cls, db_manager, carpeta_id):
        try:
            carpetas = []

            # Obtener la información de la carpeta actual
            sql = """
                SELECT nombre_carpeta, id_carpeta_padre, carpeta_id 
                FROM carpetas WHERE carpeta_id = %s
            """
            result = db_manager.execute_query(sql, (carpeta_id,))

            if not result:
                return []

            carpeta_actual = result[0]

            # Iterar para obtener todos los datos de las carpetas padre
            while carpeta_actual:
                carpeta_info = {
                    "nombre_carpeta": carpeta_actual["nombre_carpeta"],
                    "carpeta_id": carpeta_actual["carpeta_id"],
                }
                carpetas.append(carpeta_info)

                # Si no hay carpeta padre, salir del bucle
                if carpeta_actual["id_carpeta_padre"] is None:
                    break

                # Obtener la carpeta padre
                sql = """
                    SELECT nombre_carpeta, id_carpeta_padre, carpeta_id 
                    FROM carpetas WHERE carpeta_id = %s
                """
                result = db_manager.execute_query(
                    sql, (carpeta_actual["id_carpeta_padre"],)
                )
                carpeta_actual = result[0] if result else None

            return carpetas[::-1]  # Devolver la lista de carpetas en orden inverso

        except Exception as e:
            logger.error(f"Error al obtener carpeta padre: {e}")
            raise Exception(f"Error al obtener carpeta padre: {e}")

    @classmethod
    def move_folder(cls, db_manager, id_archivo, id_carpeta, dir_actual, user):
        try:
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            # Actualizar la fecha de modificación de la carpeta destino
            if id_carpeta and id_carpeta != "-1":
                sql_update_folder = """
                    UPDATE carpetas 
                    SET fecha_creacion = %s 
                    WHERE carpeta_id = %s AND id_usuario = %s
                """
                db_manager.execute_query(
                    sql_update_folder, (fecha_actual, id_carpeta, user.id)
                )

            if dir_actual and id_carpeta == "-1":
                # Obtener la carpeta actual
                sql = """
                    SELECT id_carpeta FROM archivos 
                    WHERE archivo_id = %s AND id_usuario = %s
                """
                result = db_manager.execute_query(sql, (id_archivo, user.id))

                if not result or result[0]["id_carpeta"] is None:
                    return False

                id_carpeta_resultado = result[0]["id_carpeta"]

                # Obtener la carpeta padre
                sql = """
                    SELECT id_carpeta_padre FROM carpetas 
                    WHERE carpeta_id = %s
                """
                result = db_manager.execute_query(sql, (id_carpeta_resultado,))

                if result:
                    id_carpeta = result[0]["id_carpeta_padre"]

            # Actualizar la ubicación del archivo
            if id_carpeta:
                sql = """
                    UPDATE archivos 
                    SET id_carpeta = %s, fecha_modificacion = %s 
                    WHERE archivo_id = %s AND id_usuario = %s
                """
                params = (id_carpeta, fecha_actual, id_archivo, user.id)
            else:
                sql = """
                    UPDATE archivos 
                    SET id_carpeta = NULL, fecha_modificacion = %s 
                    WHERE archivo_id = %s AND id_usuario = %s
                """
                params = (fecha_actual, id_archivo, user.id)

            db_manager.execute_query(sql, params)
            return True

        except Exception as e:
            logger.error(f"Error al mover archivo: {e}")
            raise Exception(f"Error al mover archivo: {e}")

    @classmethod
    def update_folder_timestamp(cls, db_manager, carpeta_id, user):
        """Update the timestamp of a folder to reflect content changes"""
        try:
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            sql = """
                UPDATE carpetas 
                SET fecha_creacion = %s 
                WHERE carpeta_id = %s AND id_usuario = %s
            """
            db_manager.execute_query(sql, (fecha_actual, carpeta_id, user.id))
            return True
        except Exception as e:
            logger.error(f"Error al actualizar fecha de carpeta: {e}")
            raise Exception(f"Error al actualizar fecha de carpeta: {e}")
