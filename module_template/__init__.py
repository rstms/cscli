from .cli import cli
from .context import Context
from .exception import ParameterError
from .constant import status

__all__ = ['Context' 'ParameterError', 'status', 'cli']

__name__ = '{{ project }}'
__version__ = '1.0.0'
__timestamp__ = 'yyyy-mm-dd hh:mm:ss'
__buildinfo__ = 'build system information'
__header__ = f'{__name__} v{__version__} {__timestamp__} {__buildinfo__}'
