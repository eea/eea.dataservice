class DatasetContainerView(object):
    """ Default dataset view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request