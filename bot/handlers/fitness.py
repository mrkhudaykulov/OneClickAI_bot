from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

from ..keyboards import fitness_menu, main_menu, pose_post_actions
from ..states import Fitness
from ..utils import download_best_photo_bytes
from ..services.pose import overlay_pose
from ..services.vision import analyze_calories

router = Router()


@router.message(F.text == "💪 Фитнес-камера")
async def fitness_entry(message: Message):
    await message.answer("Фитнес бўлими:", reply_markup=fitness_menu)


@router.message(F.text == "📸 Танани анализ қилиш (расм орқали)")
async def fitness_pose_request(message: Message, state):
    await state.set_state(Fitness.waiting_pose_image)
    await message.answer("Илтимос, тана позаси акс этган расм юборинг.")


@router.message(Fitness.waiting_pose_image, F.photo)
async def fitness_pose_handle(message: Message, state):
    image_bytes = await download_best_photo_bytes(message.bot, message)
    out_bytes = overlay_pose(image_bytes)
    await message.answer_photo(photo=out_bytes, caption="Скелет чизилди.", reply_markup=pose_post_actions())
    await state.clear()


@router.message(F.text == "🍛 Таом калорияси ва парҳез")
async def fitness_food(message: Message, state):
    await message.answer("Илтимос, парҳезга доир таом расмини юборинг.")
    await state.set_state(Fitness.waiting_pose_image)  # reuse for photo


@router.message(F.text == "📏 BMI / вазн / қад ҳисоблаш")
async def fitness_bmi(message: Message, state):
    await message.answer("Қад-ни қанча? см да ёзинг (масалан: 175)")
    await state.set_state(Fitness.waiting_bmi_height)


@router.message(Fitness.waiting_bmi_height, F.text.regexp(r"^\d{2,3}$"))
async def fitness_bmi_height(message: Message, state):
    await state.update_data(height_cm=int(message.text))
    await message.answer("Вазнингиз қанча? кг да ёзинг (масалан: 70)")
    await state.set_state(Fitness.waiting_bmi_weight)


@router.message(Fitness.waiting_bmi_weight, F.text.regexp(r"^\d{2,3}$"))
async def fitness_bmi_weight(message: Message, state):
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
    await message.answer("Мақсадингиз? Масалан: вазн ташлаш, мушак чиқариш, чиниқиш")
    await state.set_state(Fitness.waiting_workout_prefs)


@router.message(Fitness.waiting_workout_prefs)
async def fitness_workout_prefs(message: Message, state):
    goal = message.text or ""
    # Simple templated suggestion (no network call)
    reply = (
        f"Мақсад: {goal}\n"
        "Ҳафтасига 3-4 кун. Комплекс машқлар: squats, push-ups, rows, planks.\n"
        "Кардио: 20-30 дақиқа – yugurish/velo.\n"
        "Қувват машқларида progressive overload. Уйқу 7-8 соат."
    )
    await message.answer(reply)
    await state.clear()


@router.message(F.text == "📅 Фитнес-режа тузиш")
async def fitness_plan(message: Message, state):
    await message.answer("Қанча кунлик ва қайси ускуналар бор? Масалан: 4 кун, зал")
    await state.set_state(Fitness.waiting_plan_details)


@router.message(Fitness.waiting_plan_details)
async def fitness_plan_details(message: Message, state):
    details = message.text or ""
    plan = (
        "1-кун: Ko'krak + Triceps, 2-кун: Orqa + Biceps, 3-кун: Dam, 4-кун: Oyoq + Yelka.\n"
        "Har mashq 3-4 set, 8-12 takror. Yakunda 15-20 daqiqa kardio."
    )
    await message.answer(f"Сизнинг киритганингиз: {details}\n\nТаклиф этилган режа:\n{plan}")
    await state.clear()


@router.message(F.text == "🔙 Орқага")
async def back_to_main(message: Message, state):
    await state.clear()
    await message.answer("Асосий меню:", reply_markup=main_menu)


@router.callback_query(Text("pose_again"))
async def pose_again(cb: CallbackQuery, state):
    await cb.answer()
    await state.set_state(Fitness.waiting_pose_image)
    await cb.message.answer("Яна расм юборинг.")


@router.callback_query(Text("back_fitness_menu"))
async def back_fitness_menu(cb: CallbackQuery, state):
    await cb.answer()
    await state.clear()
    await cb.message.answer("Фитнес бўлими:", reply_markup=fitness_menu)
