// Рассчитывает НМЦК в форме

$('.prices').on('input', function () {calculate($(this));});
$('.num').on('input', function () {calculate($(this));});
//Запуск функции при загрузке страницы с инициализированными данными
$('.num').trigger('input');

function calculate(price) {
    var prices = price.parent().parent().children('.price_there');
    var price1 = Number(prices.children('.price1').val());
    var price2 = Number(prices.children('.price2').val());
    var price3 = Number(prices.children('.price3').val());
    var nums = Number(
        price.parent().parent().children('.num_there').children('.num').val()
    );

    var avrg = (price1 + price2 + price3) / 3;
    price.parent().parent().children('.avgs').text(Math.round(avrg * 100) / 100);

    var standard_deviation = Math.sqrt(
        (
            Math.pow(price1 - avrg, 2) +
            Math.pow(price2 - avrg, 2) +
            Math.pow(price3 - avrg, 2)
        ) / 2
    );

    var variation = (standard_deviation / avrg * 100).toFixed(2);
    if (variation == 'NaN') {
        variation = '0.00'
    };
    price.parent().parent().children('.variations').text(variation);

    var summs = (Math.round(avrg * 100) / 100 * nums);
    price.parent().parent().children('.summs').text(summs);

    var summ_all = 0;
    [].forEach.call($('.summs'), function(elem) {
        summ_all += Number(elem.innerText);
    });
    $('#summ_all').text(summ_all.toFixed(2))
};