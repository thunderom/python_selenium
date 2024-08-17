import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ES
from selenium.webdriver.common.action_chains import ActionChains
from helper.common import CommonHelper

# определяем константой адрес страницы для теста
URL = "https://test-shop.qa.studio/"

def test_product_view_sku(browser):
    '''
    TMS-1: [web][catalog] Проверка SKU товара "ДИВВИНА Журнальный столик"
    '''
    # переходим на тестовый сайт
    browser.get(url = URL)

	# ищем по селектору элемент меню "Бестселлеры" 
    element_bestsellers = browser.find_element(By.CSS_SELECTOR, value = '[class="tab-best_sellers "]')
    # скроллим к элементу, чтобы он оказался в видимой области
    browser.execute_script("arguments[0].scrollIntoView(true);", element_bestsellers)
    # после скроллинга можно безопасно кликнуть по элементу
    element_bestsellers.click()

	# ищем по селектору карточку "ДИВВИНА Журнальный столик"
    element_divinna = browser.find_element(By.CSS_SELECTOR, value = '[class*=post-11341]')
    # скроллим к элементу, чтобы он оказался в видимой области
    browser.execute_script("arguments[0].scrollIntoView(true);", element_divinna)
    # после скроллинга можно безопасно кликнуть по элементу, чтобы просмотреть детали
    element_divinna.click()

	# ищем по имени класса артикул для "Журнального столика"
    sku = browser.find_element(By.CLASS_NAME, value = 'sku')

	# проверяем соответствие
    assert sku.text == 'C0MSSDSUM7', "Unexpected sku"

@pytest.mark.xfail(reason = "Ожидание исправления бага 'Показано 17 из 17 товары'")
def test_count_of_all_products(browser):
    '''
    TMS-2: [web][main_page] Проверка счётчика товаров на главной странице
    '''
    # переходим на тестовый сайт
    browser.get(url = URL)

    # скроллим страницу до самого низа, чтобы подгрузить все товары на странице
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # ожидаем, пока текст "Показано 17 из 17 товаров" станет видимым, 
    # это подтверждает, что все товары загружены и отображены на странице
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.text_to_be_present_in_element(
        (By.CLASS_NAME, "razzi-posts__found-inner"), "Показано 17 из 17 товаров"))
    
    # ищем все элементы, представляющие товары на странице, по CSS-селектору
    elements = browser.find_elements(By.CSS_SELECTOR, value = '[id="rz-shop-content"] ul li')

    # проверяем, что количество найденных товаров равно 17
    assert len(elements) == 17, "Unexpected count of products"

def test_e2e(browser):
    '''
    TMS-3: [web][main_page] Проверка пути пользователя от входа на сайт до успешной покупки товара
    '''
    # переходим на тестовый сайт
    browser.get(url = URL)

    # скроллим страницу до самого низа, чтобы подгрузить все товары на странице
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # ожидаем, пока текст "Показано 17 из 17 товаров" станет видимым, 
    # это подтверждает, что все товары загружены и отображены на странице
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.text_to_be_present_in_element(
        (By.CLASS_NAME, "razzi-posts__found-inner"), "Показано 17 из 17 товары"))

	# ищем по селектору карточку "ЛЕРГРЮН Подвесной светильник"
    product = browser.find_element(By.CSS_SELECTOR, value = '[class*=post-11333] a')
    # перемещаем на неё курсор, чтобы активировать любые скрытые элементы (например, кнопки)
    ActionChains(browser).move_to_element(product).perform()
    # кликаем на неё, чтобы просмотреть детали
    product.click()

    # ожидаем, пока кнопка "В Корзину" станет кликабельной, подтверждая, что страница полностью загружена
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.element_to_be_clickable(
        (By.CSS_SELECTOR, '[name="add-to-cart"]')))

	# ищем по селектору кнопку "В Корзину" и кликаем на неё
    browser.find_element(By.CSS_SELECTOR, value = '[name="add-to-cart"]').click()

    # ожидаем появления модального окна корзины, подтверждая, что товар был добавлен в корзину
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.visibility_of_element_located(
        (By.XPATH, '//*[@id="cart-modal"]')))
    
    # проверяем, что корзина отображается корректно, её CSS-свойство "display" должно быть "block"
    cart_is_visible = browser.find_element(
        By.XPATH, value = '//*[@id="cart-modal"]').value_of_css_property("display")
    assert cart_is_visible == "block", "Unexpected state of cart"

    # кликаем на кнопку "Посмотреть корзину" в модальном окне, для перехода на страницу корзины
    browser.find_element(By.CSS_SELECTOR, value = '[class*="button wc-forward"]').click()

    # ожидаем, пока URL изменится на страницу корзины, подтверждая успешный переход
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.url_to_be(f'{URL}cart/'))

    # кликаем на кнопку "Оформить заказ", для перехода на страницу с оформлением заказа
    browser.find_element(By.XPATH, value = '//*[@id="post-9"]/div/div[2]/div/div/div/a[1]').click()

    # ожидаем, пока URL изменится на страницу оформления заказа, подтверждая успешный переход
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.url_to_be(f'{URL}checkout/'))

    # вводим данные в поля формы для оформления заказа, используя подготовленный CommonHelper
    common_helper = CommonHelper(browser)
    common_helper.enter_input(input_id = 'billing_first_name', data = 'Roman')
    common_helper.enter_input(input_id = 'billing_last_name', data = 'Grand')
    common_helper.enter_input(input_id = 'billing_address_1', data = '3-1, Wonderfull Street')
    common_helper.enter_input(input_id = 'billing_city', data = 'Novosibirsk')
    common_helper.enter_input(input_id = 'billing_state', data = 'Novosibirskaya Oblast')
    common_helper.enter_input(input_id = 'billing_postcode', data = '630001')
    common_helper.enter_input(input_id = 'billing_phone', data = '+79012345678')
    common_helper.enter_input(input_id = 'billing_email', data = 'roman@grand.ru')

    # ожидаем, что радиобаттон "Оплата при доставке" активирован
    payment = '//*[@id="payment"] [contains(@style, "position: static; zoom: 1;")]'
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.presence_of_element_located(
        (By.XPATH, payment)))
    # кликаем на кнопку "Подтвердить заказ", чтобы завершить покупку
    browser.find_element(By.ID, value = "place_order").click()

    # ожидаем, пока URL изменится на страницу с результатами оформления заказа
    WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.url_contains(f'{URL}checkout/order-received/'))

    # ожидаем появления сообщения об успешном размещении заказа и проверяем его текст
    result = WebDriverWait(browser, timeout = 10, poll_frequency = 1).until(ES.text_to_be_present_in_element(
        (By.CSS_SELECTOR, '[class="woocommerce-notice woocommerce-notice--success woocommerce-thankyou-order-received"]'), \
            "Ваш заказ принят. Благодарим вас."))
    
    # проверяем, что сообщение об успешном заказе отображается корректно
    assert result, "Unexpected notification text"
