$(".paste_img").each(function(){
  if($(this).prev().text() == '' || $(this).prev().text() == 'None'){
    $(this).hide();
  }
  $(this).click(function(){
    $(this).next().show();
    $('.Copied').not($(this).next()).hide();
    var a = $(this).prev().text();
    if (navigator.clipboard !== undefined){
      navigator.clipboard.writeText(a);
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = a;
      document.body.appendChild(textArea);
      textArea.select();
      textArea.setSelectionRange(0, 99999);
      try {
        document.execCommand('copy');
      } catch (err) {
        console.error('복사 실패', err);
      }
      textArea.setSelectionRange(0, 0);
      document.body.removeChild(textArea);
    }
  });
});

$(".status_text").each(function(){
  var a = $(this).text();
  $(this).parent('span').addClass(a);
})

$(".sort").each(function(){
$(".sort").off().click(function() {
  var $table = $(this).parents('.caseTable');
  var $tbody = $table.find("tbody");
  var $rows = $tbody.find("tr").toArray();

  var sortOrder = $(this).attr("sort-order");
  if (sortOrder === "asc") {
    $(this).attr("sort-order", "desc");
    $rows.sort(function(a, b) {
      var aValue = $(a).find(".result .status_text").text();
      var bValue = $(b).find(".result .status_text").text();
      return aValue.localeCompare(bValue);
    });
  } else {
    $(this).attr("sort-order", "asc");
    $rows.sort(function(a, b) {
      var aValue = $(a).find(".result .status_text").text();
      var bValue = $(b).find(".result .status_text").text();
      return bValue.localeCompare(aValue);
    });
  }

  $.each($rows, function(index, row) {
    $tbody.append(row);
  });
});

});



$(".command_icon").each(function(){
  if($(this).next().text() == '' || $(this).next().text() == 'None'){
    $(this).hide();
  }
  $(".command_icon").off().click(function(){
    $(this).next().fadeToggle(300)
  });
});


$(".commit").each(function(){
  if($(this).text() == 'None' ){
    $(this).text('');
  };
});

$(".search_list_name").each(function(){
    $('.search_list_name').off().click(function(){
      if (!$(event.target).is('.show_all')) {
        $(this).children('.show_all').slideToggle();
        $(this).next().slideToggle();
      }
    });
});


$(".search_li").each(function(){
  $('.search_li').off().click(function(){
    $(this).next().slideToggle();
  });
});

$(".show_all").each(function(){
  $('.show_all').off().click(function(){
    var caseTable = $(this).parent().next().find('.caseTable');
    caseTable.toggle(caseTable.css('display') === 'none');
  });
});


$('.show_all_case').off().click(function(){
  var search_list = $(this).parent().find('.search_case');
  search_list.toggle(search_list.css('display') === 'none');
});