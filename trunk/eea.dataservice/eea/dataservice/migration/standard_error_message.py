#  you could easily check for the error_type and
#  dispatch to an appropriate PageTemplate.

error_type=kwargs.get('error_type', None)
error_message=kwargs.get('error_message', None)
error_log_url=kwargs.get('error_log_url', None)
error_tb=kwargs.get('error_tb', None)
error_traceback=kwargs.get('error_traceback', None)
error_value=kwargs.get('error_value', None)

error_page=None

# Check with redirection tool if error type is NotFound
if error_type == 'NotFound':
    catalog = context.portal_catalog
    requested_file = context.REQUEST.get('URL', '').split('/')[-1]

    # To match dataservice shortId and UID
    if context.getId() == 'data':
        # UID resquest
        query = {'portal_type': 'Data',
                 'UID': requested_file}
        res = catalog(query)
        if len(res) > 0:
            redirect_to = context.absolute_url() + '/' + res[0].getId
            return context.REQUEST.RESPONSE.redirect(redirect_to, lock=1)
        # ShortID request
        query = {'portal_type': 'Data',
                 'getShortId': context.REQUEST.get('id', '')}
        res = catalog(query)
        if len(res) > 0:
            redirect_to = context.absolute_url() + '/' + res[0].getId
            return context.REQUEST.RESPONSE.redirect(redirect_to, lock=1)

    # To match old reports.eea.europa.eu links
    query = {'object_provides' : 'eea.reports.interfaces.IReportContainerEnhanced',
             'getId': context.getId()}
    if len(catalog(query)) > 0:
        redirect_to = context.absolute_url()
        mainfile_id = context.get('file').filename
        if mainfile_id == requested_file:
            redirect_to = context.absolute_url() + '/at_download/file'
        return context.REQUEST.RESPONSE.redirect(redirect_to, lock=1)

    error_page=context.not_found_message(error_type=error_type,
                                         error_message=error_message,
                                         error_tb=error_tb,
                                         error_value=error_value)

else:
    error_page=context.default_error_message(error_type=error_type,
                                             error_message=error_message,
                                             error_tb=error_tb,
                                             error_value=error_value)

return error_page
