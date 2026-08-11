import logging
from datetime import datetime, timezone

import aiosqlite

from config import DATABASE_FILE


logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    Crea la base de datos y las tablas necesarias.

    Este método se ejecuta cuando el bot arranca.
    """

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        # Tabla de progreso por juego.
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS game_progress (
                user_id INTEGER NOT NULL,
                game_id TEXT NOT NULL,
                current_room TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, game_id)
            )
            """
        )

        # Tabla para recordar cuál fue el último juego usado por el jugador.
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS player_state (
                user_id INTEGER PRIMARY KEY,
                last_game_id TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )

        # Tabla de flags por jugador y juego.
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS game_flags (
                user_id INTEGER NOT NULL,
                game_id TEXT NOT NULL,
                flag TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, game_id, flag)
            )
            """
        )

        # Migración automática desde la tabla antigua si existe.
        cursor = await db.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='player_progress'
            """
        )

        old_table_exists = await cursor.fetchone()

        if old_table_exists:
            await db.execute(
                """
                INSERT OR IGNORE INTO game_progress (
                    user_id,
                    game_id,
                    current_room,
                    updated_at
                )
                SELECT
                    user_id,
                    current_game,
                    current_room,
                    updated_at
                FROM player_progress
                WHERE current_game IS NOT NULL
                  AND current_room IS NOT NULL
                """
            )

            await db.execute(
                """
                INSERT OR IGNORE INTO player_state (
                    user_id,
                    last_game_id,
                    updated_at
                )
                SELECT
                    user_id,
                    current_game,
                    updated_at
                FROM player_progress
                WHERE current_game IS NOT NULL
                """
            )

        await db.commit()

    logger.info("Base de datos inicializada correctamente.")


async def save_progress(user_id: int, game_id: str, room_id: str) -> None:
    """
    Guarda el progreso de un jugador en un juego.

    Si el jugador ya tenía progreso en ese juego, lo actualiza.
    También guarda cuál fue el último juego jugado.
    """

    if not game_id or not room_id:
        return

    updated_at = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        await db.execute(
            """
            INSERT INTO game_progress (
                user_id,
                game_id,
                current_room,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, game_id) DO UPDATE SET
                current_room = excluded.current_room,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                game_id,
                room_id,
                updated_at,
            ),
        )

        await db.execute(
            """
            INSERT INTO player_state (
                user_id,
                last_game_id,
                updated_at
            )
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                last_game_id = excluded.last_game_id,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                game_id,
                updated_at,
            ),
        )

        await db.commit()


async def get_game_progress(user_id: int, game_id: str):
    """
    Devuelve la habitación guardada de un jugador en un juego concreto.

    Si no existe, devuelve None.
    """

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        cursor = await db.execute(
            """
            SELECT current_room
            FROM game_progress
            WHERE user_id = ?
              AND game_id = ?
            """,
            (
                user_id,
                game_id,
            ),
        )

        row = await cursor.fetchone()

        if row:
            return row[0]

        return None


async def get_last_game_id(user_id: int):
    """
    Devuelve el último juego jugado por un jugador.

    Si no existe, devuelve None.
    """

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        cursor = await db.execute(
            """
            SELECT last_game_id
            FROM player_state
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()

        if row:
            return row[0]

        return None


async def set_flag(user_id: int, game_id: str, flag: str) -> None:
    """
    Guarda un flag para un jugador en un juego.

    Si el flag ya existe, no lo duplica.
    """

    if not game_id or not flag:
        return

    updated_at = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        await db.execute(
            """
            INSERT INTO game_flags (
                user_id,
                game_id,
                flag,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, game_id, flag) DO UPDATE SET
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                game_id,
                flag,
                updated_at,
            ),
        )

        await db.commit()


async def get_flags(user_id: int, game_id: str):
    """
    Devuelve la lista de flags que tiene un jugador en un juego.
    """

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        cursor = await db.execute(
            """
            SELECT flag
            FROM game_flags
            WHERE user_id = ?
              AND game_id = ?
            """,
            (
                user_id,
                game_id,
            ),
        )

        rows = await cursor.fetchall()

        return [row[0] for row in rows]


async def clear_progress(user_id: int) -> None:
    """
    Borra todo el progreso de un jugador.

    Esto incluye:
    - progreso de habitaciones
    - último juego jugado
    - flags
    """

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        await db.execute(
            """
            DELETE FROM game_progress
            WHERE user_id = ?
            """,
            (user_id,),
        )

        await db.execute(
            """
            DELETE FROM player_state
            WHERE user_id = ?
            """,
            (user_id,),
        )

        await db.execute(
            """
            DELETE FROM game_flags
            WHERE user_id = ?
            """,
            (user_id,),
        )

        await db.commit()


async def clear_game_progress(user_id: int, game_id: str) -> None:
    """
    Borra solo el progreso de un juego concreto.

    Esto incluye:
    - progreso de habitaciones de ese juego
    - flags de ese juego
    - último juego jugado, si era este mismo juego
    """

    if not user_id or not game_id:
        return

    async with aiosqlite.connect(str(DATABASE_FILE)) as db:

        await db.execute(
            """
            DELETE FROM game_progress
            WHERE user_id = ?
              AND game_id = ?
            """,
            (
                user_id,
                game_id,
            ),
        )

        await db.execute(
            """
            DELETE FROM game_flags
            WHERE user_id = ?
              AND game_id = ?
            """,
            (
                user_id,
                game_id,
            ),
        )

        await db.execute(
            """
            DELETE FROM player_state
            WHERE user_id = ?
              AND last_game_id = ?
            """,
            (
                user_id,
                game_id,
            ),
        )

        await db.commit()