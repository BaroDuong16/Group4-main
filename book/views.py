import requests
from django.core.paginator import Paginator
from django.shortcuts import render

def book_search_view(request):
    query = request.GET.get('q', '')
    book_type = request.GET.get('book_type', 'free')
    books_per_page = 5 

    books = []
    total_items = 0

    # Initialize page_number
    page_number = request.GET.get('page', 1)  # Default to page 1 if not provided

    if query:
        if book_type == 'free':
            api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&filter=free-ebooks&maxResults=40&key=AIzaSyBxsqMKP8XrSsdzAX0Kx-uJzHZ8lIredT4"
        else:
            api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&key=AIzaSyCpskMxoV94c32BqyhGce6JJLuHQ4bZjJg"

        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            total_items = data.get('totalItems', 0)

            # Fetching the books based on the total items available
            if 'items' in data:
                for item in data['items']:
                    volume_info = item.get('volumeInfo', {})
                    book = {
                        'title': volume_info.get('title', 'No title available'),
                        'authors': volume_info.get('authors', ['Unknown author']),
                        'description': volume_info.get('description', 'No description available'),
                        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', None),
                        'infoLink': volume_info.get('infoLink', '#'),
                        'previewLink': volume_info.get('previewLink', '#'),
                        'publisher': volume_info.get('publisher', 'Unknown publisher'),
                        'publishedDate': volume_info.get('publishedDate', 'Unknown date'),
                    }
                    books.append(book)

        # Create a new paginator for the full list of books
        paginator = Paginator(books, books_per_page)  
        paginated_books = paginator.get_page(page_number)  

        # Fetch more results from the API if there are more pages
        if paginator.num_pages > 1:
            for page in range(2, paginator.num_pages + 1):
                start_index = (page - 1) * 40  # Calculate the startIndex for subsequent pages
                api_url_paginated = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&startIndex={start_index}&key=AIzaSyCpskMxoV94c32BqyhGce6JJLuHQ4bZjJg"
                response_paginated = requests.get(api_url_paginated)

                if response_paginated.status_code == 200:
                    data_paginated = response_paginated.json()
                    if 'items' in data_paginated:
                        for item in data_paginated['items']:
                            volume_info = item.get('volumeInfo', {})
                            book = {
                                'title': volume_info.get('title', 'No title available'),
                                'authors': volume_info.get('authors', ['Unknown author']),
                                'description': volume_info.get('description', 'No description available'),
                                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', None),
                                'infoLink': volume_info.get('infoLink', '#'),
                                'previewLink': volume_info.get('previewLink', '#'),
                                'publisher': volume_info.get('publisher', 'Unknown publisher'),
                                'publishedDate': volume_info.get('publishedDate', 'Unknown date'),
                            }
                            books.append(book)

    else:
        # If no query, return an empty paginated list
        paginator = Paginator([], books_per_page)
        paginated_books = paginator.get_page(page_number)

    return render(request, 'book_search.html', {
        'books': paginated_books,  # Pass the paginated books to the template
        'query': query,
        'total_items': total_items,
        'book_type': book_type,
        'paginator': paginator,  # Pass the paginator to the template
    })


def book_detail_view(request, book_id):
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
    book = response.json() if response.status_code == 200 else None
    return render(request, 'book_detail.html', {'book': book})

