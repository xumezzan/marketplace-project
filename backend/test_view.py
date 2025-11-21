from django.shortcuts import render


def test_view(request):
    """Test view to verify template rendering."""
    context = {
        'test_variable': 'Hello World',
    }
    return render(request, 'test_template.html', context)
