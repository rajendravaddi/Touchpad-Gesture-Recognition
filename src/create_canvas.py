from PIL import Image, ImageDraw
import json
import recognization_gesture_model as rgm
'''def draw(coordinates,output_image_path='data/perform.jpeg'):
    image = Image.new("RGB", (300, 170), "white")
    draw = ImageDraw.Draw(image)
    for x, y in coordinates:
        scaled_x = x/10
        scaled_y = y/10
        draw.ellipse((scaled_x , scaled_y , scaled_x + 5, scaled_y + 5), fill="black")
    image.save(output_image_path, "JPEG")
    return rgm.match_already_exists(output_image_path)
    #print(coordinates)


'''
def draw(coordinates, output_image_path='../data/perform.jpeg'):
    # Create an empty image
    image = Image.new("RGB", (300, 170), "white")
    draw = ImageDraw.Draw(image)

    # Scale coordinates to fit within the image dimensions
    scaled_coordinates = [(x / 10, y / 10) for x, y in coordinates]

    # Draw the continuous path connecting the scaled coordinates with a thicker line
    if len(scaled_coordinates) > 1:
        draw.line(scaled_coordinates, fill="black", width=5)  # Set width to match the oval size

    # Save the resulting image
    image.save(output_image_path, "JPEG")
    return rgm.match_already_exists(output_image_path)

    

