from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram import F

from ..keyboards import fitness_menu, main_menu, pose_post_actions
from ..monetization import ensure_user_and_gate
from ..states import Fitness
from ..utils import download_best_photo_bytes, to_data_url
# from ..services.pose import overlay_pose
from ..services.vision import analyze_calories
from ..services.text_gpt import generate_workout_tips, generate_week_plan, diet_from_photo_or_text

router = Router()


@router.message(F.text == "💪 Фитнес-камера")
async def fitness_entry(message: Message):
    if not await ensure_user_and_gate(message, consume=False):
        return
    await message.answer("Фитнес бўлими:", reply_markup=fitness_menu)


@router.message(F.text == "📸 Танани анализ қилиш (расм орқали)")
async def fitness_pose_request(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.set_state(Fitness.waiting_pose_image)
    await message.answer(
        "Муҳим эслатма: Танангизни умумий таҳлил қилиш учун, илтимос, тўлиқ гавдангиз акс этган расмни юборинг (спорт кийимида бўлганингиз маъқул).\n"
        "Махфийлик кафолати: Сиз юборган расм фақат бир марталик таҳлил учун ишлатилади ва тизимда сақланмайди. Натижалар тиббий ташхис эмас.")


@router.message(Fitness.waiting_pose_image, F.photo)
async def fitness_pose_handle(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    image_bytes = await download_best_photo_bytes(message.bot, message)
    await message.answer("⏳ Расм қабул қилинди. Таҳлил қилинмоқда, илтимос, бироз кутинг...")
    out_bytes = overlay_pose(image_bytes)
    # ✅ Shu yerda to‘g‘rilaymiz:
    photo_file = BufferedInputFile(out_bytes, filename="pose_result.jpg")
    analysis = (
        "Умумий таҳлил натижалари:\n"
        "Қомат ҳолати: Елкалар бироз олдинга етилиши мумкин.\n"
        "Тахминий тана тури: Қўшимча машқ ва ovqatlanish bilan yaxshilanishi mumkin."
    )
    await message.answer_photo(photo=photo_file, caption=analysis, reply_markup=pose_post_actions())
    await state.clear()


@router.message(F.text == "🍛 Таом калорияси ва парҳез")
async def fitness_food(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await message.answer("Таом расмини юборинг ёки таомни матнда ёзинг (масалан: 'палов 1 порция').")
    await state.set_state(Fitness.waiting_diet_input)


@router.message(Fitness.waiting_diet_input, F.photo)
async def fitness_diet_photo(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    image_bytes = await download_best_photo_bytes(message.bot, message)
    await message.answer("⏳ Расм қабул қилинди. Таҳлил қилинмоқда...")
    hint = analyze_calories(to_data_url(image_bytes))
    diet = diet_from_photo_or_text(hint)
    await message.answer(f"{hint}\n\nПарҳез бўйича маслаҳат:\n{diet}")
    await state.clear()


@router.message(Fitness.waiting_diet_input, F.text)
async def fitness_diet_text(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    hint = message.text or ""
    diet = diet_from_photo_or_text(hint)
    await message.answer(f"Таҳлил: {hint}\n\nПарҳез бўйича маслаҳат:\n{diet}")
    await state.clear()


@router.message(F.text == "📏 BMI / вазн / қад ҳисоблаш")
async def fitness_bmi(message: Message, state):
    if not await ensure_user_and_gate(message, consume=False):
        return
    await message.answer("Қад-ни қанча? см да ёзинг (масалан: 175)")
    await state.set_state(Fitness.waiting_bmi_height)


@router.message(Fitness.waiting_bmi_height, F.text.regexp(r"^\d{2,3}$"))
async def fitness_bmi_height(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.update_data(height_cm=int(message.text))
    await message.answer("Вазнингиз қанча? кг да ёзинг (масалан: 70)")
    await state.set_state(Fitness.waiting_bmi_weight)


@router.message(Fitness.waiting_bmi_weight, F.text.regexp(r"^\d{2,3}$"))
async def fitness_bmi_weight(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    data = await state.get_data()
    height_cm = data.get("height_cm")
    weight_kg = int(message.text)
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    category = (
        "Ортиқча озғун" if bmi < 18.5 else
        "Нормал" if bmi < 25 else
        "Ортиқча вазн" if bmi < 30 else
        "Семизлик"
    )

    await message.answer(f"BMI: <b>{bmi}</b> — {category}")
    await state.clear()


@router.message(F.text == "🏃 Машқ тавсиялари")
async def fitness_workout(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await message.answer("Мақсадингиз? Масалан: вазн ташлаш, мушак чиқариш, чиниқиш")
    await state.set_state(Fitness.waiting_workout_prefs)


@router.message(Fitness.waiting_workout_prefs)
async def fitness_workout_prefs(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.update_data(goal=message.text or "")
    await state.set_state(Fitness.waiting_workout_place)
    await message.answer("Қаерда машқ қиласиз? (уйда/зал)")


@router.message(Fitness.waiting_workout_place)
async def fitness_workout_place(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    data = await state.get_data()
    goal = data.get("goal", "")
    place = message.text or ""
    reply = generate_workout_tips(goal, place)
    await message.answer(reply)
    await state.clear()


@router.message(F.text == "📅 Фитнес-режа тузиш")
async def fitness_plan(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await message.answer("Қанча кунлик ва қайси ускуналар бор? Масалан: 4 кун, зал")
    await state.set_state(Fitness.waiting_plan_details)


@router.message(Fitness.waiting_plan_details)
async def fitness_plan_details(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    details = message.text or ""
    plan = generate_week_plan(details)
    await message.answer(f"Сизнинг киритганингиз: {details}\n\nТаклиф этилган режа:\n{plan}")
    await state.clear()


@router.message(F.text == "🔙 Орқага")
async def back_to_main(message: Message, state):
    await state.clear()
    await message.answer("Асосий меню:", reply_markup=main_menu)


@router.callback_query(F.data == "pose_again")
async def pose_again(cb: CallbackQuery, state):
    await cb.answer()
    await state.set_state(Fitness.waiting_pose_image)
    await cb.message.answer("Яна расм юборинг.")


@router.callback_query(F.data == "back_fitness_menu")
async def back_fitness_menu(cb: CallbackQuery, state):
    await cb.answer()
    await state.clear()
    await cb.message.answer("Фитнес бўлими:", reply_markup=fitness_menu)
