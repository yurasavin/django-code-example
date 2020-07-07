// Предварительно должен быть загружен calculate.js
// Добавляет в форму дополнительные строки

$(function() {
    $("#add_rows").click(function() {
        var rows_count = $('.positions').length;
        var start = rows_count;
        rows_count += 10;
        $('#id_form-TOTAL_FORMS').val(rows_count);
        for (curr_row_num = start; curr_row_num < rows_count; curr_row_num++) {
            $(".positions:last").after(
                '<tr class="positions"><td>' + (curr_row_num + 1) + '</td>\
                 <td><input type="text" name="form-'+ curr_row_num + '-name" form="positions_form" id="id_form-'+ curr_row_num + '-name"></td>\
                 <td><input type="text" name="form-'+ curr_row_num + '-type_of_size" form="positions_form" id="id_form-'+ curr_row_num + '-type_of_size"></td>\
                 <td class="num_there"><input type="number" name="form-'+ curr_row_num + '-num" form="positions_form" step="0.1" class="num" id="id_form-'+ curr_row_num + '-num"></td>\
                 <td class="price_there"><input type="number" name="form-'+ curr_row_num + '-price1" form="positions_form" step="0.01" class="prices price1" id="id_form-'+ curr_row_num + '-price1"></td>\
                 <td class="price_there"><input type="number" name="form-'+ curr_row_num + '-price2" form="positions_form" step="0.01" class="prices price2" id="id_form-'+ curr_row_num + '-price2"></td>\
                 <td class="price_there"><input type="number" name="form-'+ curr_row_num + '-price3" form="positions_form" step="0.01" class="prices price3" id="id_form-'+ curr_row_num + '-price3"></td>\
                 <td class="avgs"></td>\
                 <td class="variations"></td>\
                 <td class="summs"></td></tr>\
                '
            );
        };
        $('.prices').on('input', function () {calculate($(this));});
        $('.num').on('input', function () {calculate($(this));});
    });
});
