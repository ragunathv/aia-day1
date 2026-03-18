import aiohttp
from aiohttp import web
import json
import time

OLLAMA_URL = 'http://localhost:11434'

async def proxy_handler(request):
    path = request.match_info.get('path', '')
    url = f'{OLLAMA_URL}/api/{path}'

    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers.items() if k.lower() not in ['host']},
            data=await request.read(),
            params=request.query
        ) as resp:
            # Check if streaming
            is_streaming = resp.headers.get('transfer-encoding') == 'chunked' or 'text/plain' in str(resp.headers.get('content-type', ''))

            if is_streaming:
                # Handle streaming response
                response = web.StreamResponse()
                response.headers.update(resp.headers)
                await response.prepare(request)

                data_lines = []
                async for chunk in resp.content:
                    data_lines.append(chunk)
                    await response.write(chunk)

                # After stream ends, parse the last line for token info
                if data_lines:
                    try:
                        # Combine all chunks and split by lines
                        full_data = b''.join(data_lines).decode('utf-8')
                        lines = full_data.strip().split('\n')
                        if lines:
                            last_line = lines[-1]
                            if last_line:
                                last_json = json.loads(last_line)
                                if 'prompt_eval_count' in last_json:
                                    model = last_json.get('model', 'unknown')
                                    prompt_tokens = last_json.get('prompt_eval_count', 0)
                                    generated_tokens = last_json.get('eval_count', 0)
                                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Operation: {path}, Model: {model}, Prompt tokens: {prompt_tokens}, Generated tokens: {generated_tokens}")
                    except Exception as e:
                        print(f"Error parsing token info: {e}")

                return response
            else:
                # Non-streaming response
                content = await resp.read()
                try:
                    json_data = json.loads(content.decode('utf-8'))
                    if 'prompt_eval_count' in json_data:
                        model = json_data.get('model', 'unknown')
                        prompt_tokens = json_data.get('prompt_eval_count', 0)
                        generated_tokens = json_data.get('eval_count', 0)
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Operation: {path}, Model: {model}, Prompt tokens: {prompt_tokens}, Generated tokens: {generated_tokens}")
                except:
                    pass

                return web.Response(body=content, headers=resp.headers)

app = web.Application()
app.router.add_route('*', '/api/{path:.*}', proxy_handler)

if __name__ == '__main__':
    print("Starting Ollama Token Monitor on port 11435...")
    print("Point your Ollama client to http://localhost:11435")
    web.run_app(app, host='0.0.0.0', port=11435)
