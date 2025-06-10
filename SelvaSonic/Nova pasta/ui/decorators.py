<<<<<<< HEAD
from functools import wraps
from typing import Callable

def validate_positive(func: Callable) -> Callable:
    """
    Decorador para validar que todos os parâmetros numéricos são positivos.

    Args:
        func (Callable): Função a ser decorada.

    Returns:
        Callable: Função decorada que lança ValueError para valores negativos.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verifica todos os argumentos posicionais e nomeados
        for arg in list(args) + list(kwargs.values()):
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Parâmetro negativo detectado: {arg}")
        return func(*args, **kwargs)
=======
from functools import wraps
from typing import Callable

def validate_positive(func: Callable) -> Callable:
    """
    Decorador para validar que todos os parâmetros numéricos são positivos.

    Args:
        func (Callable): Função a ser decorada.

    Returns:
        Callable: Função decorada que lança ValueError para valores negativos.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verifica todos os argumentos posicionais e nomeados
        for arg in list(args) + list(kwargs.values()):
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Parâmetro negativo detectado: {arg}")
        return func(*args, **kwargs)
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    return wrapper