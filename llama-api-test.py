import requests, json

def completion_streaming(prompt: str):
    # Access the llama-server API running locally and get the completion of a prompt
    url = "http://localhost:8080/v1/chat/completions"
    data = {
        "model": "llama-2-7b.Q3_K_L.gguf",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
            ],
        "temperature": 0.9,
        "max_tokens": 50,
        "stop": ["user", "system"],  # Stop on these tokens, which limits the response to a single message
        "stream": True
    }
    with requests.post(url, json=data, stream=True) as response:
        for line in response.iter_lines(decode_unicode=True):
            line = line[6:]
            if line and line != '[DONE]':
                try:
                    print(json.loads(line)['choices'][0]['delta']['content'], end='', flush=True)
                except KeyError:
                    continue
                except json.JSONDecodeError:
                    print("ERROR:", line)



def completion(prompt: str):
    # Access the llama-server API running locally and get the completion of a prompt
    url = "http://localhost:8080/v1/chat/completions"
    data = {
        "model": "llama-2-7b.Q3_K_L.gguf",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
            ],
        "temperature": 0.9,
        "max_tokens": 50,
        "stop": ["user", "system"]  # Stop on these tokens, which limits the response to a single message
    }
    response = requests.post(url, json=data)
    response_json = response.json()
    print(response_json['choices'][0]['message']['content'])

completion_streaming("What is the capital of Angola?")

