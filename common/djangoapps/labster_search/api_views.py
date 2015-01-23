from rest_framework.response import Response
from rest_framework.views import APIView


class Search(APIView):

    def get(self, request, *args, **kwargs):
        keywords = request.GET.get('q', "").lower().strip()
        response = {
            'keyword': keywords,
            'total': 0,
            'results': [],
        }

        if keywords:
            results = []
            response.update({
                'total': len(results),
            })

        return Response(response)
