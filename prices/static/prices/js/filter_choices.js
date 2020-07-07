// Прячет последующие значения если пусто текущее при загрузке страницы
// if ($('select[name="year"]').val() == 'default'){
//     $('select[name="source"] optgroup').hide();
//     $('select[name="article"] optgroup').hide();
//     $('select[name="industry_code"] optgroup').hide();
//     $('select[name="limit_money"] optgroup').hide();
//     $('select[name="subdivision"] optgroup').hide();
// } else if ($('select[name="source"]').val() == 'default'){
//     $('select[name="article"] optgroup').hide();
//     $('select[name="industry_code"] optgroup').hide();
//     $('select[name="limit_money"] optgroup').hide();
//     $('select[name="subdivision"] optgroup').hide();
// } else if ($('select[name="article"]').val() == 'default'){
//     $('select[name="industry_code"] optgroup').hide();
//     $('select[name="limit_money"] optgroup').hide();
// } else if ($('select[name="industry_code"]').val() == 'default'){
//     $('select[name="limit_money"] optgroup').hide();
// };

var selected_id = $('select[name="year"]').val();
$('select[name="source"] optgroup').hide();
$('select[name="source"] optgroup').filter(function(){
    var group_name = $(this).attr('label');
    return group_name == selected_id;
}).show();


var selected_id = $('select[name="source"]').val();
$('select[name="article"] optgroup').hide();
$('select[name="article"] optgroup').filter(function(){
    var group_name = $(this).attr('label');
    return group_name == selected_id;
}).show();


var selected_id = $('select[name="source"]').val();
$('select[name="subdivision"] optgroup').hide();
$('select[name="subdivision"] optgroup').filter(function(){
    var group_name = $(this).attr('label');
    return group_name == selected_id;
}).show();


var selected_id = $('select[name="article"]').val();
$('select[name="industry_code"] optgroup').hide();
$('select[name="industry_code"] optgroup').filter(function(){
    var group_name = $(this).attr('label');
    return group_name == selected_id;
}).show();


var selected_id = $('select[name="industry_code"]').val();
$('select[name="limit_money"] optgroup').hide();
$('select[name="limit_money"] optgroup').filter(function(){
    var group_name = $(this).attr('label');
    return group_name == selected_id;
}).show();


// Фильтрует элементы при выборе года
$('select[name="year"]').change(function(){
    var selected_id = $(this).val();
    // Фильтруем источники
    $('select[name="source"] optgroup').hide();
    $('select[name="source"] optgroup').filter(function(){
        var group_name = $(this).attr('label');
        return group_name == selected_id;
    }).show();
    $('select[name="source"]').val('default');
});


// Фильтрует элементы при выборе источника
$('select[name="source"]').change(function(){
    var selected_id = $(this).val();
    // фильтруем статьи
    $('select[name="article"] optgroup').hide();
    $('select[name="article"] optgroup').filter(function(){
        var group_name = $(this).attr('label');
        return group_name == selected_id;
    }).show();
    $('select[name="article"]').val('default');
    // Фильтруем подразделы
    $('select[name="subdivision"] optgroup').hide();
    $('select[name="subdivision"] optgroup').filter(function(){
        var group_name = $(this).attr('label');
        return group_name == selected_id;
    }).show();
    $('select[name="subdivision"]').val('default');
});


// Фильтрует элементы при выборе статьи
$('select[name="article"]').change(function(){
    var selected_id = $(this).val();
    $('select[name="industry_code"] optgroup').hide();
    $('select[name="industry_code"] optgroup').filter(function(){
        var group_name = $(this).attr('label');
        return group_name == selected_id;
    }).show();
    $('select[name="industry_code"]').val('default');
});


// Фильтрует элементы при выборе отраслевого кода
$('select[name="industry_code"]').change(function(){
    var selected_id = $(this).val();
    $('select[name="limit_money"] optgroup').hide();
    $('select[name="limit_money"] optgroup').filter(function(){
        var group_name = $(this).attr('label');
        return group_name == selected_id;
    }).show();
    $('select[name="limit_money"]').val('default');
});
