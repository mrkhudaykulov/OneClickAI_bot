# import numpy as np
# import cv2
# import mediapipe as mp
from io import BytesIO

# mp_pose = mp.solutions.pose
# mp_drawing = mp.solutions.drawing_utils
# mp_styles = mp.solutions.drawing_styles


# def overlay_pose(image_bytes: bytes) -> bytes:
#     np_arr = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#     if img is None:
#         raise ValueError("Invalid image data")
# 
#     with mp_pose.Pose(static_image_mode=True, enable_segmentation=False) as pose:
#         result = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#         if result.pose_landmarks:
#             mp_drawing.draw_landmarks(
#                 img,
#                 result.pose_landmarks,
#                 mp_pose.POSE_CONNECTIONS,
#                 landmark_drawing_spec=mp_styles.get_default_pose_landmarks_style(),
#             )
# 
#     success, encoded = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
#     if not success:
#         raise RuntimeError("Failed to encode image")
#     return encoded.tobytes()
