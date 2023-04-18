$(function () {
  $(".has_sub").click(function () {
      $(".left_sub_menu").fadeToggle(300);
  });
  $(".click_top").each(function(){
    $('.click_top').off().click(function(){
      $(this).parent().find('.big_menu').slideToggle();
    });
  });
  $(".click_big").each(function(){
    $('.click_big').off().click(function(){
      $(this).parent().find('.small_menu').slideToggle();
    });
  });

  function getListData(num, url){
    $.ajax({
      type : "GET",
      url : `/${url}/${num}`,
      dataType : 'html',
      cache : false,
      success : function(data){
        $('.overlay').html(data);
      },
      error : function(data){
        alert(`Server error! id:${num}`);
      }
    });
  }

  $(".real_time").each(function(){
    $('.real_time').off().click(function(){
      var id = $(this).closest('ul').attr('id');
      getListData(id, 'details');
    });
  });

  $(".failed_list").each(function(){
    $('.failed_list').off().click(function(){
      var id = $(this).closest('ul').attr('id');
      getListData(id, 'failed');
    });
  });

  $(".weekly_chart").each(function(){
    $('.weekly_chart').off().click(function(){
      var id = $(this).attr('id');
      getListData(id, 'weekly');
    });
  });

  $('.chart').easyPieChart({
    size: 400,
    barColor: "#FF6384",
    scaleLength: 0,
    lineWidth: 40,
    trackColor: "#373737",
    lineCap: "circle",
    animate: 600,
  });

  function getPreviousSelect(num){
    $.ajax({
      type : "GET",
      url : `/index_selectbox/${num}`,
      dataType : 'json',
      cache : false,
      success : function(data){
        var selectbox = $("<select name='build_date'>");
        for (var i=0; i<data.build_dates.length; i++) {
            var option = $("<option>").text(data.build_dates[i]);
            option.val(data.build_dates[i]);
            selectbox.append(option);
        }
        $("select[name=build_date]").remove();
        $("#previous_button").before(selectbox);
      },
      error : function(data){
        alert(`Error Build_Date!`);
      }
    });
  }

  var selectbox = $("select[name='project']")
  selectbox.change(function(){
    var id = $(this).val()
    getPreviousSelect(id)
  });
  selectbox.trigger("change")

  function getPreviousData(num, build_date){
    $.ajax({
      type : "GET",
      url : `/get_previous/${num}/${build_date}`,
      dataType : 'html',
      cache : false,
      success : function(data){
        $('.overlay').html(data);
      },
      error : function(data){
        alert(`Server error! id:${num}, build_date:${build_date}`);
      }
    });
  }

  $('#previous_button').click(function(){
    var id = $("select[name=project]").val();
    var build_date = $("select[name=build_date]").val();
    getPreviousData(id, build_date);
  });

  var selectedValue = $('input[type=radio][name=chk]:checked').val();
  $('input[type=radio][name=chk]').change(function() {
    selectedValue = $(this).val();
  });

  // 자동 완성을 구현할 입력 상자 선택
  $("#test_name").autocomplete({
    source: function(request, response) {
      if (selectedValue == 'LIST'){
        var url = "autocomplete_list"
      } else {
        var url = "autocomplete_case"
      }
      var num = $("select[name=project_search]").val();
      $.ajax({
        url: `/${url}/${num}`,
        dataType: "json",
        data: {
          term: request.term
        },
        success: function(data) {
          response(data.map(function(item) {
            if (url == "autocomplete_list") {
              return item.ListName;
            }
            else {
              return item.CaseName
            }
          }));
        }
      });
    },
    minLength: 2 // 자동 완성 최소 글자 수
  });
});


function getSearchData(num, test_name, url){
  $.ajax({
    type : "GET",
    url : `/${url}/${num}/${test_name}`,
    dataType : 'html',
    cache : false,
    success : function(data){
      $('.overlay').html(data);
    },
    error : function(data){
      alert(`Server error! id:${num}, build_date:${build_date}`);
    }
  });
}

$("#test_name").on("keyup", function(event) {
  if (event.keyCode === 13) { // `ENTER` keyCode
    $("#search_button").click();
  }
});

$('#search_button').click(function(){
  var id = $("select[name=project_search]").val();
  var test_name = $("#test_name").val();
  if ($('input[type=radio][name=chk]:checked').val() == 'LIST'){
    var url = 'search_list';
  } else {
    var url = 'search_case';
  }
  getSearchData(id, test_name,url);
});