import cv2
import face_recognition
from functions import ai_response

# Initialize boolean to check for my face
findingRay = True

# Load my face image and learn how to recognize it
known_image = face_recognition.load_image_file("C:\\Users\\Raypo\\OneDrive\\Pictures\\Camera Roll\\my_face.jpg")

# Attempt to get face encodings
known_face_encodings = face_recognition.face_encodings(known_image)

# Check if any face encodings were found
if not known_face_encodings:
    raise ValueError("No face encodings found in the image.")

# Get the first face encoding
known_face_encoding = known_face_encodings[0]

# Initialize variables for find_ray()
face_locations = []
face_encodings = []
face_names = []

def find_ray():
    global findingRay

    video_capture = cv2.VideoCapture(0)

    while findingRay:
        # Capture a single frame of video
        ret, frame = video_capture.read()

        # Resize the frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Only process every other frame to improve performance
        if cv2.waitKey(1) & 0xFF != ord('q'):
            # Find all the faces and face encodings in the frame
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)
            face_names = []

            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces([known_face_encoding], face_encoding)
                name = "Unknown"
                if match[0]:
                    name = "Ray Poulton"
                    findingRay = False
                    print("Ray Identified")
                    ai_response("You're no longer in sleep mode. Feel free to prompt me about our previous conversation, or whatever I need help with.")
                    break  # Stop processing once the face is found
                face_names.append(name)

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


