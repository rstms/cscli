"""Top-level package for cscli."""

__author__ = """Matt Krueger"""
__email__ = "mkrueger@rstms.net"
__version__ = "0.3.4"
__description__ = "CloudSigma API command line interface"
__timestamp__ = "2021-09-16T02:07:07-05:00"

from .api_client import CloudSigmaClient

MIN_CPU = 1
MIN_MHZ = 1000
MIN_RAM = "256M"
MIN_DISK = "512M"

PASSWORD_LEN = 24

__all__ = [CloudSigmaClient]
