

let search_button = document.getElementById('search_button');
let search_text_input = document.getElementById('search_text');
let sorting_input = document.getElementById('sort_by');
let count_of_cards_input = document.getElementById('count_of_cards');
let offset_input = document.getElementById('offset');

function search() {
	let search_text = search_text_input.value

	if (search_text !== '') {
		console.log(search_text)

		const parsing_schema = {
			search_text: search_text,
			count_of_cards: count_of_cards_input.value,
			sorting: sorting_input.value,
			offset: offset_input.value,
		}

		console.log(parsing_schema)

		// Показываем анимацию загрузки
		document.getElementById('loading').style.display = 'block'

		fetch('/parsing', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(parsing_schema),
		})
			.then(response => {
				if (!response.ok) {
					throw new Error('Сеть ответа не в порядке')
				}
				return response.json()
			})
			.then(data => {
				console.log('Успешный ответ:', data)
                displayCards(data.cards)
			})
			.catch(error => {
				console.error('Ошибка при запросе:', error)
			})
			.finally(() => {
				// Скрываем анимацию загрузки после завершения запроса
				document.getElementById('loading').style.display = 'none'
			})
	}
}

function displayCards(cards) {
	// Получаем контейнер для карточек
	const cardsContainer = document.getElementById('cardsContainer')
	cardsContainer.innerHTML = '' // Очищаем контейнер перед добавлением карточек

	// Проходим по массиву карточек и создаем элементы
	cards.forEach(card => {
		const cardElement = document.createElement('div')
		cardElement.classList.add('product-card') // Класс для стилизации карточки

		// Заполняем карточку данными
		cardElement.innerHTML = `
            <div class="card-image">
                <img src="${card.main_photo}" alt="${card.title}" />
            </div>
            <div class="card-content">
                <h2 class="card-title">${card.title}</h2>
                <p class="card-description">${card.description}</p>
                <p class="card-price"><strong>Цена: </strong>${card.ozon_card_price} ₽</p>
                <p class="card-discount"><strong>Скидка: </strong>${card.discounted_price} ₽</p>
                <p class="card-rating"><strong>Рейтинг: </strong>${card.rating} (${card.count_of_reviews} отзывов)</p>
                <p class="card-seller"><strong>Продавец: </strong><a href="${card.seller_url}">${card.seller_name}</a></p>
                <p class="card-deliver-date"><strong>Дата доставки: </strong>${card.deliver_date}</p>
                <a href="${card.url}" target="_blank" class="card-button">Смотреть товар</a>
            </div>
        `

		// Добавляем карточку в контейнер
		cardsContainer.appendChild(cardElement)
	})
}


search_button.addEventListener('click', () => {
    search();
})

