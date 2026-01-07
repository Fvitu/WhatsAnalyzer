from .entities.User import User
from datetime import datetime
import pytz  # Add this import
from flask import request
import logging

logger = logging.getLogger("model_user")


class ModelUser:
    @classmethod
    def register(cls, db_manager, user):
        try:
            # Obtener la fecha actual
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            # Obtener la IP del usuario
            ip_usuario = request.remote_addr

            # Obtener el valor máximo de la columna id y sumarle 1
            max_id = db_manager.execute_query("SELECT MAX(id) as max_id FROM user")[0][
                "max_id"
            ]
            nuevo_id = max_id + 1 if max_id is not None else 1

            # Utilizar parámetros para prevenir inyección SQL
            sql = """INSERT INTO user 
                    (id, username, password, email, ip, fecha_logueo, fecha_registro) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            params = (
                nuevo_id,
                user.username,
                User.convert_password(user.password),
                user.email,
                ip_usuario,
                fecha_actual,
                fecha_actual,
            )

            db_manager.execute_query(sql, params)
            return user
        except Exception as e:
            logger.error(f"Error en registro de usuario: {e}")
            raise Exception(f"Error al registrar usuario: {e}")

    @classmethod
    def login(cls, db_manager, user):
        try:
            # Utilizar parámetros para prevenir inyección SQL
            sql = "SELECT id, username, password, email FROM user WHERE username = %s"
            result = db_manager.execute_query(sql, (user.username,))

            if result:
                row = result[0]
                # Obtener la fecha actual
                tz = pytz.timezone("America/Argentina/Buenos_Aires")
                fecha_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

                # Actualizar fecha de login
                sql2 = "UPDATE user SET fecha_logueo = %s WHERE id = %s"
                db_manager.execute_query(sql2, (fecha_actual, row["id"]))

                user = User(
                    row["id"],
                    row["username"],
                    User.check_password(row["password"], user.password),
                    row["email"],
                )
                return user
            else:
                return None
        except Exception as e:
            logger.error(f"Error en login: {e}")
            raise Exception(f"Error en autenticación: {e}")

    @classmethod
    def is_email_taken(cls, db_manager, email):
        try:
            sql = "SELECT id FROM user WHERE email = %s"
            result = db_manager.execute_query(sql, (email,))
            return bool(
                result
            )  # True si el correo electrónico está en uso, False de lo contrario
        except Exception as e:
            logger.error(f"Error al verificar email: {e}")
            raise Exception(f"Error al verificar disponibilidad de email: {e}")

    @classmethod
    def get_by_id(cls, db_manager, id):
        try:
            sql = "SELECT id, username, email FROM user WHERE id = %s"
            result = db_manager.execute_query(sql, (id,))

            if result:
                row = result[0]
                return User(row["id"], row["username"], None, row["email"])
            else:
                return None
        except Exception as e:
            logger.error(f"Error al obtener usuario por ID: {e}")
            # En este método específico, maneja la excepción de manera especial
            # ya que es llamado por el login_manager y fallas aquí afectan toda la aplicación
            logger.error(f"Retornando None para evitar error crítico: {e}")
            return None  # Retorna None en lugar de propagar la excepción
