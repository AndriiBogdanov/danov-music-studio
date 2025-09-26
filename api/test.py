def handler(request, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Vercel Python Test - Working!</h1>'
    } 