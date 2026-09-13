import ollama

response = ollama.chat(
    model="phi3:mini",
    messages=[
        {"role": "user", "content": "Say hello as MediVault AI assistant"}
    ]
)

<<<<<<< HEAD
print(response['message']['content'])
=======
print(response['message']['content'])
>>>>>>> ce28435f31caa3ab7a8c4ca182d2c9317b6e51dd
