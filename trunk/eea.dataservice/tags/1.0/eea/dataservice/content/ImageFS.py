# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.validation import V_REQUIRED
from Products.CMFCore.permissions import View
from plone.app.blob.field import BlobField
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema
from plone.app.blob.mixins import ImageFieldMixin
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.atapi import registerType
from plone.app.blob.interfaces import IBlobImageField
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.image import ATImage
from Products.Archetypes.public import PrimaryFieldMarshaller
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from eea.dataservice.config import *
from eea.dataservice.interfaces import IImageFS


class ImageBlobField(BlobField, ImageFieldMixin):
    """ derivative of blobfield for extending schemas """
    implements(IBlobImageField)

    def set(self, instance, value, **kwargs):
        super(ImageBlobField, self).set(instance, value, **kwargs)
        self.fixAutoId(instance)

    def getAvailableSizes(self, instance):
        return self.sizes

imagefs_schema = ATContentTypeSchema.copy() + Schema((
    ImageBlobField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
               pil_quality = zconf.pil_config.quality,
               pil_resize_algo = zconf.pil_config.resize_algo,
               max_size = zconf.ATImage.max_image_dimension,
               sizes= {'large'   : (768, 768),
                       'preview' : (400, 400),
                       'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkImageMaxSize', V_REQUIRED)),
               widget = ImageWidget(
                        #description = "Select the image to be added by clicking the 'Browse' button.",
                        #description_msgid = "help_image",
                        description = "",
                        label= "Image",
                        label_msgid = "label_image",
                        i18n_domain = "plone",
                        show_content_type = False,)),

    ), marshall=PrimaryFieldMarshaller()
    )

finalizeATCTSchema(imagefs_schema)

class ImageFS(ATImage):
    """ ImageFS Content Type
    """
    implements(IImageFS)
    security = ClassSecurityInfo()

    archetype_name  = 'ImageFS'
    portal_type     = 'ImageFS'
    meta_type       = 'ImageFS'
    _at_rename_after_creation = True

    schema = imagefs_schema


    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline or as an attachment """
        field = self.getPrimaryField()
        return field.index_html(self, REQUEST, RESPONSE)


registerType(ImageFS, PROJECTNAME)
