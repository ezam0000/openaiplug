import quart
import quart_cors
from quart import request, jsonify

app = quart_cors.cors(quart.Quart(__name__), allow_origin="*")

@app.route("/defeat", methods=["POST"])
async def defeat_ai():
    data = await request.get_json()
    api_key = data.get("api_key")
    input_text = data.get("input_text")

    if not api_key:
        return jsonify({"error": "API Key is required."}), 400

    url = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "text-davinci-003",
        "prompt": input_text,
        "temperature": 0.87,
        "max_tokens": 400,
        "top_p": 1.0,
        "frequency_penalty": 1.44,
        "presence_penalty": 1.29
    }

    async with quart.current_app.async_client.post(url, headers=headers, json=payload) as response:
        if response.status_code == 200:
            try:
                text = (await response.get_json())["choices"][0]["text"]
                paragraphs = text.split("\n")
                return jsonify({"response": paragraphs})
            except KeyError as e:
                return jsonify({"error": f"Error: Failed to parse response JSON: {e}"}), 500
        elif response.status_code == 400:
            error_message = (await response.get_json()).get("error", "Unknown error")
            error_code = (await response.get_json()).get("code", "Unknown code")
            return jsonify({"error": f"Error: Bad request: {error_message} ({error_code})"}), 400
        elif response.status_code == 401:
            return jsonify({"error": "Error: Authentication failed. Please check your API key."}), 401
        elif response.status_code == 429:
            return jsonify({"error": "Error: API rate limit exceeded. Please wait and try again later."}), 429
        else:
            return jsonify({"error": f"Error: Failed to generate text: {response.status_code} {response.reason}"}), 500

@app.route("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await quart.send_file(filename, mimetype="image/png")

@app.route("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.route("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5001)

if __name__ == "__main__":
    main()
