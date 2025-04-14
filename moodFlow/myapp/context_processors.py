from datetime import datetime

def global_context(request):
    return {
        'year': datetime.now().year
    }