from google import genai
client = genai.Client(api_key='')
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Explain Boyce Codd Normal Form in simple terms.'
)
print(response.text)
