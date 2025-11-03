import moondream as md
from PIL import Image
import json

# Initialize with API key
model = md.vl(api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlfaWQiOiI2YzE2YjAzNy1jMjA4LTQzNjgtYjYwZS0wZGUzM2Q5MDdmNmEiLCJvcmdfaWQiOiJXV0ZlbkJFWXptYVR6ZXZ4RlZrbWI3Um9ZQUhuRzB4MSIsImlhdCI6MTc1ODgzMjc4OSwidmVyIjoxfQ.gEThxMDn73Wkvu57OU8agKf1DQH3lymqZqKzTieEBSE")

# Load an image
image = Image.open("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/frame1.jpg")

# results = []
# # Ask a question
# answer = model.query(image, """inside this image is a UFC fight, I need you to find the TIME CLOCK!!!! inside the TIME CLOCK its should 
#                      the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
#                      something to remember is sometimes you wont see a TIME CLOCK at all and sometimes the fight the will be in between
#                      rounds as well that means you should return a 'null' value in json format else
#                      Return the time and rnd in json format""")["answer"]

# results.append(answer)

# # save all responses in one JSON file
# with open("results.json", "w") as f:
#     json.dump(results, f, indent=2)

# Detect objects (e.g., "person", "car", "face", etc.)
result = model.detect(image, "time clock")

detections = result["objects"]
print(f"Found {len(detections)} clock")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Assuming 'image' is the PIL Image object from your existing code
# and 'detections' is the list of detection dictionaries.

# Get image dimensions
width, height = image.size

# Create figure and axes
fig, ax = plt.subplots(1)

# Display the image
ax.imshow(image)

# Process and draw each bounding box
for detection in detections:
    # Scale the bounding box coordinates
    x_min = detection['x_min'] * width
    y_min = detection['y_min'] * height
    x_max = detection['x_max'] * width
    y_max = detection['y_max'] * height

    # Create a Rectangle patch
    rect = patches.Rectangle(
        (x_min, y_min),
        x_max - x_min,
        y_max - y_min,
        linewidth=1,
        edgecolor='r',
        facecolor='none'
    )

    # Add the patch to the Axes
    ax.add_patch(rect)

# Show the plot
plt.show()
















