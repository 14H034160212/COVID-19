from functools import wraps


def logged(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging

@logged
def f(x):
   """does some math"""
   return x + x * x

#print(f.__name__)  # prints 'f'
#print(f.__doc__)   # prints 'does some math'


articles_per_page = 3
len = 8


cursor = articles_per_page * int(len / articles_per_page)
if len % articles_per_page == 0:
    print('decreemnting')
    cursor -= articles_per_page
print(cursor)
