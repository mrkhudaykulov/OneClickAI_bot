from aiogram.fsm.state import StatesGroup, State

class PhotoServices(StatesGroup):
    waiting_image = State()  # mode in data: calories|recipe|ocr|product
    waiting_ocr_edit = State()
    waiting_translation_lang = State()

class Fitness(StatesGroup):
    waiting_pose_image = State()
    waiting_diet_input = State()
    waiting_bmi_height = State()
    waiting_bmi_weight = State()
    waiting_workout_prefs = State()
    waiting_workout_place = State()
    waiting_plan_details = State()
