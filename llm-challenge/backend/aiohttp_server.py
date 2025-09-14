from aiohttp import web
import json

async def health(request):
    return web.Response(
        text=json.dumps({"status": "healthy", "message": "Backend is running"}),
        content_type='application/json',
        headers={'Access-Control-Allow-Origin': '*'}
    )

app = web.Application()
app.router.add_get('/health', health)

if __name__ == '__main__':
    print("Starting backend server on http://localhost:8000")
    web.run_app(app, host='0.0.0.0', port=8000)