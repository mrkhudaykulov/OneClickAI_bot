from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

from ..keyboards import photo_services_menu, calories_post_actions, recipe_post_actions, ocr_post_actions, product_post_actions, main_menu
from ..monetization import ensure_user_and_gate
from ..states import PhotoServices
from ..utils import download_best_photo_bytes, to_data_url
from ..services.vision import analyze_calories, identify_recipe, identify_product
from ..services.ocr import ocr_image_to_text
from ..services.translate import translate_text
from ..services.files import text_to_pdf_bytes, text_to_docx_bytes

router = Router()


# Entry point to photo services
@router.message(F.text == "📷 Расм орқали хизматлар")
async def photo_menu(message: Message):
    if not await ensure_user_and_gate(message, consume=False):
        return
    await message.answer("Хизмат турини танланг:", reply_markup=photo_services_menu)


# Calories
@router.message(F.text == "🍔 Калория аниқлаш")
async def calories_entry(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="calories")
    await message.answer(
        "Жуда яхши! Таомнинг калориясини аниқлаш учун унинг аниқ ва сифатли туширилган расмини юборинг.\n"
        "Илтимос, иложи борича битта порция расмини юборинг.")


@router.message(PhotoServices.waiting_image, F.photo)
async def handle_waiting_image(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    data = await state.get_data()
    mode = data.get("mode")
    image_bytes = await download_best_photo_bytes(message.bot, message)
    data_url = to_data_url(image_bytes)

    if mode == "calories":
        await message.answer("⏳ Расм қабул қилинди. Таҳлил қилинмоқда, илтимос, бироз кутинг...")
        result = analyze_calories(data_url)
        # Enrich with CTA lines per spec
        extra = ("\nБугунги калория меъёрингизни билиш учун \"Фитнес-камера\" бўлимидан фойдаланинг.\n"
                 "Кейинги ҳаракатни танланг:")
        await message.answer(result + "\n" + extra, reply_markup=calories_post_actions())
        return

    if mode == "recipe":
        await message.answer("⏳ Таҳлил қилинмоқда... Сиз учун энг яхши рецептни қидирмоқдаман.")
        result = identify_recipe(data_url)
        await message.answer(result, reply_markup=recipe_post_actions())
        return

    if mode == "ocr":
        text = ocr_image_to_text(data_url)
        await state.update_data(ocr_text=text)
        await message.answer(f"Матн аниқланди:\n{text}\n\nНима қиламиз?", reply_markup=ocr_post_actions())
        return

    if mode == "product":
        await message.answer("⏳ Таҳлил қилинмоқда... Объектни аниқлаяпман.")
        result = identify_product(data_url)
        await message.answer(result, reply_markup=product_post_actions())
        return


# Recipe
@router.message(F.text == "🍽 Таомни таниш + рецепт бериш")
async def recipe_entry(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="recipe")
    await message.answer("Таом расмини юборинг.")


# OCR
@router.message(F.text == "🧾 Матнни OCR орқали текстга айлантириш")
async def ocr_entry(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="ocr")
    await message.answer("Матнли расмни юборинг. Масалан: ҳужжат, қоғоз, экран скриншоти ва ҳ.к.")


# Product
@router.message(F.text == "🛍 Объект/товарни таниш")
async def product_entry(message: Message, state):
    if not await ensure_user_and_gate(message):
        return
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="product")
    await message.answer("Илтимос, объект ёки товар расмини юбортинг.")


# Back buttons
@router.message(F.text == "🔙 Орқага")
async def back_to_main(message: Message, state):
    await state.clear()
    await message.answer("Асосий менюга қайтдингиз.", reply_markup=main_menu)


# Inline callbacks for calories
@router.callback_query(Text("calories_again"))
async def calories_again(cb: CallbackQuery, state):
    await cb.answer()
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="calories")
    await cb.message.answer("Яна таом расмини юборинг.")


@router.callback_query(Text("calories_more"))
async def calories_more(cb: CallbackQuery, state):
    await cb.answer()
    data = await state.get_data()
    # For demo: reuse last result if needed. In real app, store structured data.
    await cb.message.answer("Статистика: ҳозирча демонстрация режимида.")


# Inline callbacks for recipe
@router.callback_query(Text("recipe_again"))
async def recipe_again(cb: CallbackQuery, state):
    await cb.answer()
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="recipe")
    await cb.message.answer("Бошқа таом расмини юборинг.")


@router.callback_query(Text("recipe_check_calories"))
async def recipe_check_calories(cb: CallbackQuery, state):
    await cb.answer()
    await state.set_state(PhotoServices.waiting_image)
    await state.update_data(mode="calories")
    await cb.message.answer("Худди шу таом учун калорияни текшириш. Илтимос, расм юборинг.")


# Inline callbacks for OCR
@router.callback_query(Text("ocr_make_files"))
async def ocr_make_files(cb: CallbackQuery, state):
    await cb.answer()
    data = await state.get_data()
    text = data.get("ocr_text", "")
    if not text:
        await cb.message.answer("Бирор матн топилмади. Илтимос, аввал расм юборинг.")
        return
    pdf_bytes = text_to_pdf_bytes(text)
    docx_bytes = text_to_docx_bytes(text)
    await cb.message.answer_document(document=("ocr.pdf", pdf_bytes))
    await cb.message.answer_document(document=("ocr.docx", docx_bytes))


@router.callback_query(Text("ocr_translate"))
async def ocr_translate(cb: CallbackQuery, state):
    await cb.answer()
    await state.set_state(PhotoServices.waiting_translation_lang)
    await cb.message.answer("Қайси тилга таржима қиламиз? Масалан: EN, RU, UZ-LATIN")


@router.callback_query(Text("ocr_edit"))
async def ocr_edit(cb: CallbackQuery, state):
    await cb.answer()
    await cb.message.answer("Янги таҳрирланган матнни юборинг.")
    await state.set_state(PhotoServices.waiting_ocr_edit)


@router.message(PhotoServices.waiting_ocr_edit)
async def ocr_edit_receive(message: Message, state):
    await state.update_data(ocr_text=message.text or "")
    await state.clear()
    await message.answer("Сақланди. Қандай давом этамиз?", reply_markup=photo_services_menu)


@router.message(PhotoServices.waiting_translation_lang)
async def ocr_receive_lang(message: Message, state):
    lang = (message.text or "").strip()
    data = await state.get_data()
    text = data.get("ocr_text", "")
    if not text:
        await state.clear()
        await message.answer("Аввал OCR матни йўқ. Илтимос, расм юборинг.", reply_markup=photo_services_menu)
        return
    translated = translate_text(text, lang)
    await state.clear()
    await message.answer(translated, reply_markup=photo_services_menu)


# Back inline to menu
@router.callback_query(Text("back_photo_menu"))
async def back_photo_menu(cb: CallbackQuery, state):
    await cb.answer()
    await state.clear()
    await cb.message.answer("Хизмат турини танланг:", reply_markup=photo_services_menu)
