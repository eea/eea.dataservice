""" PIL plugins
"""
from PIL.EpsImagePlugin import _accept
from PIL import Image
from eea.dataservice.pil.EpsImagePlugin import EpsImageFile

def register():
    """ Register PIL Plugins
    """
    Image.register_open(EpsImageFile.format, EpsImageFile, _accept)

