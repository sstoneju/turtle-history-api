def hello_function(request, context):
    """
    $ echo '{"function_name":"hello","args":{"hello":"world"}}' | http ':3001' --debug
    $ echo '{"function_name": "hello", "args":{"hello":"world"}' | sam local invoke "HelloWorldFunction" --debug
    """
    return { 'args':f'{request}', 'context':f'{context}'}
