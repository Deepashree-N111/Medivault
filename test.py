import ollama

response = ollama.chat(
    model="phi3:mini",
    messages=[
        {"role": "user", "content": "Say hello as MediVault AI assistant"}
    ]
)

print(response['message']['content'])
