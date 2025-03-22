import streamlit as st
import requests
from PIL import Image
import io
import base64
import time
from utils.client_logger import ClientLogger

def main():
    logger = ClientLogger()
    logger.info("Запуск приложения")
    
    st.title("SRGAN Апскейлер Изображений")
    st.write("Загрузите изображение для увеличения разрешения")

    # Загрузка изображения
    uploaded_file = st.file_uploader("Выберите изображение", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        logger.log_upload(uploaded_file.name, uploaded_file.size)
        
        try:
            # Показать оригинальное изображение
            image = Image.open(uploaded_file)
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Оригинальное изображение")
                st.image(image, use_column_width=True)
                logger.log_ui_action("Отображено оригинальное изображение")

            # Кнопка для обработки
            if st.button("Увеличить разрешение"):
                logger.log_ui_action("Нажата кнопка увеличения разрешения")
                try:
                    start_time = time.time()
                    uploaded_file.seek(0)
                    
                    # Подготовка файла для отправки
                    files = {
                        "file": ("image.png", uploaded_file.read(), "image/png")
                    }
                    
                    # Отправка запроса на API
                    with st.spinner("Обработка изображения..."):
                        logger.info("Отправка запроса на сервер")
                        response = requests.post(
                            "https://ba6b-89-39-107-196.ngrok-free.app/upscale",
                            files=files,
                            data={"scale_factor": 4}
                        )
                    
                    process_time = time.time() - start_time
                    logger.log_response(response.status_code, process_time)
                    
                    if response.status_code == 200:
                        result = response.json()
                        image_data = base64.b64decode(result["image"])
                        upscaled_image = Image.open(io.BytesIO(image_data))
                        
                        with col2:
                            st.subheader("Обработанное изображение")
                            st.image(upscaled_image, use_column_width=True)
                            logger.info("Успешно отображено обработанное изображение")
                    else:
                        error_msg = f"Ошибка при обработке: {response.status_code}"
                        logger.error(f"{error_msg}\nДетали: {response.text}")
                        st.error(error_msg)
                        st.error(f"Детали: {response.text}")
                        
                except Exception as e:
                    error_msg = f"Ошибка при обработке запроса: {str(e)}"
                    logger.log_error(e, "обработка_запроса")
                    st.error(error_msg)
        
        except Exception as e:
            error_msg = f"Ошибка при открытии изображения: {str(e)}"
            logger.log_error(e, "открытие_изображения")
            st.error(error_msg)

if __name__ == "__main__":
    main()