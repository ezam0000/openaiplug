import os
import quart
import quart_cors
from quart import request, jsonify

app = quart.Quart(__name__)
app = quart_cors.cors(app)

@app.post("/defeat")
async def defeat_ai():
    data = await request.get_json()
    api_key = data.get("api_key")
    input_text = data.get("input_text")

    if not api_key:
        return quart.Response("API Key is required.", status=400)

    url = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4",
        "prompt": input_text,
        "temperature": 0.87,
        "max_tokens": 400,
        "top_p": 1.0,
        "frequency_penalty": 1.44,
        "presence_penalty": 1.29
    }

    response = await quart.current_app.async_client.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            text = response.json()["choices"][0]["text"]
            paragraphs = text.split("\n")
            return jsonify({"response": paragraphs})
        except KeyError as e:
            return quart.Response(f"Error: Failed to parse response JSON: {e}", status=500)
    elif response.status_code == 400:
        error_message = response.json().get("error", "Unknown error")
        error_code = response.json().get("code", "Unknown code")
        return quart.Response(f"Error: Bad request: {error_message} ({error_code})", status=400)
    elif response.status_code == 401:
        return quart.Response("Error: Authentication failed. Please check your API key.", status=401)
    elif response.status_code == 429:
        return quart.Response("Error: API rate limit exceeded. Please wait and try again later.", status=429)
    else:
        return quart.Response(f"Error: Failed to generate text: {response.status_code} {response.reason}", status=500)

@app.get("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await quart.send_file(filename, mimetype="image/png")

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    main()
