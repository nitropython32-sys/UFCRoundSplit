import moondream as md
from PIL import Image
from config import API_KEY

# connect to Moondream Station
# Initialize for Moondream Cloud
model = md.vl(api_key=API_KEY)

# Load an image
image = Image.open("frame_135s.jpg")


# Ask a question
answer = model.query(image, """inside this image is a UFC fight, I need you to find the time clock. inside the time clock its should 
                     the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
                     Return the time and rnd in json format""")["answer"]
print("Answer:", answer)


