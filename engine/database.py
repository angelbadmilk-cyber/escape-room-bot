import logging
import os
from datetime import datetime, timezone

import asyncpg

from config import DATABASE_URL


logger = logging.getLogger(__name__)


# Pool de conexiones reutilizable (más eficiente que abrir y cerrar en cada consulta).
_pool = None


import ssl

# ... (el resto de imports arriba se mantiene igual)

async def _get_pool():
    """
    Devuelve el pool de conexiones, creándolo si no existe todavía.
    Fuerza SSL y desactiva verificaciones estrictas para evitar problemas
    con IPv6 y certificados en entornos como Render.
    """
    global _pool
    if _pool is None:
        # Contexto SSL relajado para evitar errores de red en Render
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        _pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=1,
            max_size=5,
            command_timeout=60,
            ssl=ssl_context,
        )
    return _pool


async def init_db() -> None:
    """
    Crea las tablas necesarias en PostgreSQL si no existen.
    Se ejecuta cuando el bot arranca.
    """

    pool = await _get_pool()

    async with pool.acquire() as conn:

        # Tabla de progreso por juego.
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS game_progress (
                user_id BIGINT NOT NULL,
                game_id TEXT NOT NULL,
                current_room TEXT NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL,
                PRIMARY KEY (user_id, game_id)
            )
            """
        )

        # Tabla para recordar cuál fue el último juego usado por el jugador.
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_state (
                user_id BIGINT PRIMARY KEY,
                last_game_id TEXT,
                updated_at TIMESTAMPTZ NOT NULL
            )
            """
        )

        # Tabla de flags por jugador y juego.
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS game_flags (
                user_id BIGINT NOT NULL,
                game_id TEXT NOT NULL,
                flag TEXT NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL,
                PRIMARY KEY (user_id, game_id, flag)
            )
            """
        )

    logger.info("Base de datos PostgreSQL (Supabase) inicializada correctamente.")


async def save_progress(user_id: int, game_id: str, room_id: str) -> None:
    """
    Guarda el progreso de un jugador en un juego.
    """

    if not game_id or not room_id:
        return

    updated_at = datetime.now(timezone.utc)

    pool = await _get_pool()

    async with pool.acquire() as conn:

        await conn.execute(
            """
            INSERT INTO game_progress (
                user_id,
                game_id,
                current_room,
                updated_at
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, game_id) DO UPDATE SET
                current_room = EXCLUDED.current_room,
                updated_at = EXCLUDED.updated_at
            """,
            user_id,
            game_id,
            room_id,
            updated_at,
        )

        await conn.execute(
            """
            INSERT INTO player_state (
                user_id,
                last_game_id,
                updated_at
            )
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET
                last_game_id = EXCLUDED.last_game_id,
                updated_at = EXCLUDED.updated_at
            """,
            user_id,
            game_id,
            updated_at,
        )


async def get_game_progress(user_id: int, game_id: str):
    """
    Devuelve la habitación guardada de un jugador en un juego concreto.
    Si no existe, devuelve None.
    """

    pool = await _get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT current_room
            FROM game_progress
            WHERE user_id = $1
              AND game_id = $2
            """,
            user_id,
            game_id,
        )

        if row:
            return row["current_room"]

        return None


async def get_last_game_id(user_id: int):
    """
    Devuelve el último juego jugado por un jugador.
    Si no existe, devuelve None.
    """

    pool = await _get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT last_game_id
            FROM player_state
            WHERE user_id = $1
            """,
            user_id,
        )

        if row:
            return row["last_game_id"]

        return None


async def set_flag(user_id: int, game_id: str, flag: str) -> None:
    """
    Guarda un flag para un jugador en un juego.
    Si el flag ya existe, no lo duplica.
    """

    if not game_id or not flag:
        return

    updated_at = datetime.now(timezone.utc)

    pool = await _get_pool()

    async with pool.acquire() as conn:

        await conn.execute(
            """
            INSERT INTO game_flags (
                user_id,
                game_id,
                flag,
                updated_at
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, game_id, flag) DO UPDATE SET
                updated_at = EXCLUDED.updated_at
            """,
            user_id,
            game_id,
            flag,
            updated_at,
        )


async def get_flags(user_id: int, game_id: str):
    """
    Devuelve la lista de flags que tiene un jugador en un juego.
    """

    pool = await _get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch(
            """
            SELECT flag
            FROM game_flags
            WHERE user_id = $1
              AND game_id = $2
            """,
            user_id,
            game_id,
        )

        return [row["flag"] for row in rows]


async def clear_progress(user_id: int) -> None:
    """
    Borra todo el progreso de un jugador.
    """

    pool = await _get_pool()

    async with pool.acquire() as conn:

        await conn.execute(
            "DELETE FROM game_progress WHERE user_id = $1",
            user_id,
        )

        await conn.execute(
            "DELETE FROM player_state WHERE user_id = $1",
            user_id,
        )

        await conn.execute(
            "DELETE FROM game_flags WHERE user_id = $1",
            user_id,
        )


async def clear_game_progress(user_id: int, game_id: str) -> None:
    """
    Borra solo el progreso de un juego concreto.
    """

    if not user_id or not game_id:
        return

    pool = await _get_pool()

    async with pool.acquire() as conn:

        await conn.execute(
            "DELETE FROM game_progress WHERE user_id = $1 AND game_id = $2",
            user_id,
            game_id,
        )

        await conn.execute(
            "DELETE FROM game_flags WHERE user_id = $1 AND game_id = $2",
            user_id,
            game_id,
        )

        await conn.execute(
            "DELETE FROM player_state WHERE user_id = $1 AND last_game_id = $2",
            user_id,
            game_id,
        )