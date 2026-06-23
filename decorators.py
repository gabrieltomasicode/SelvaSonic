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
        """
        Wrapper que verifica se todos os argumentos numéricos são positivos.

        Args:
            *args: Argumentos posicionais da função original.
            **kwargs: Argumentos nomeados da função original.

        Raises:
            ValueError: Se algum argumento numérico for negativo.
        """
        # Verifica todos os argumentos posicionais e nomeados
        for arg in list(args) + list(kwargs.values()):
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Parâmetro negativo detectado: {arg}")
        return func(*args, **kwargs)
    return wrapper