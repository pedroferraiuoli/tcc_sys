#!/usr/bin/env python
import os
import sys


def main() -> None:
    """Ponto de entrada para comandos de gerenciamento do Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc_tagger.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar Django. Certifique-se de que ele está instalado "
            "e disponível no seu PYTHONPATH, e que você ativou o ambiente virtual."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

