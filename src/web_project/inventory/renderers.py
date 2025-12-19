from rest_framework.renderers import JSONRenderer

class StandardResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None

        # Check for 204 No Content
        if response and response.status_code == 204:
            return super().render(data, accepted_media_type, renderer_context)

        response_data = {'data': None, 'meta': {}, 'errors': []}

        if response and response.exception:
             # If an exception occurred (e.g. Validation Error, Auth Error)
             # data is likely the error details
             response_data['errors'] = data if isinstance(data, list) else [data]
        else:
             # Success
             if isinstance(data, dict) and 'results' in data and 'count' in data:
                 # Pagination handling
                 response_data['data'] = data['results']
                 response_data['meta'] = {
                     'count': data['count'],
                     'next': data['next'],
                     'previous': data['previous']
                 }
             else:
                 response_data['data'] = data

        return super().render(response_data, accepted_media_type, renderer_context)
