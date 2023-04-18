$(document).ready(function(){
  function getCaseData(num, obj){
    $.ajax({
      type : "GET",
      url : `/cases/${num}`,
      dataType : 'html',
      cache : false,
      success : function(data){
        $(obj).parent().next().find('.caseTable').html(data);
      },
      error : function(data){
        alert(`Server error! id:${num}`);
      }
    });
  }
  function getPreviousCaseData(num, obj, build_date){
    $.ajax({
      type : "GET",
      url : `/previous_cases/${num}/${build_date}`,
      dataType : 'html',
      cache : false,
      success : function(data){
        $(obj).parent().next().find('.caseTable').html(data);
      },
      error : function(data){
        alert(`Server error! id:${num}`);
      }
    });
  }
  $(".IPName").each(function(){
    $('.IPName').off().click(function(){
      var id = $(this).attr('id');
      $(this).parent().next().fadeToggle(100);
      if($('#previous_span').text() == 'previous'){
        var previous_date = $('#previous_date').text();
        getPreviousCaseData(id, this, previous_date);
      } else {
        getCaseData(id, this);
      }
    });
  });
  $(".Ratio").each(function(){
    total = parseInt($(this).parent().find('.total').text());
    passed = parseInt($(this).parent().find('.passed').text());
    ratio = parseInt(passed/total*100) + "(%)";
    $(this).text(ratio);

    if($(this).text() == 'NaN(%)'){
      $(this).text('0(%)');
    }
  });
  $(".failed").each(function(){
    if($(this).text() != '0'){
      $(this).parent().find('.Name').css("background-color","rgb(255, 188, 185)")
    }
  });


  var Ttotal = 0;
  var Tpassed = 0;
  var Tfailed = 0;
  var Trunning = 0;
  var Tpending = 0;

  // tbody 열의 합 계산
  $('.total').each(function() {
    Ttotal += parseInt($(this).text());
  });
  $('.passed').each(function() {
    Tpassed += parseInt($(this).text());
  });
  $('.failed').each(function() {
    Tfailed += parseInt($(this).text());
  });
  $('.running').each(function() {
    Trunning += parseInt($(this).text());
  });
  $('.pending').each(function() {
    Tpending += parseInt($(this).text());
  });
  // 결과 출력
  $('#TTotal').text(Ttotal);
  $('#TPassed').text(Tpassed);
  $('#TFailed').text(Tfailed);
  $('#TRunning').text(Trunning);
  $('#TPending').text(Tpending);
  var TRatio = parseInt(Tpassed/Ttotal*100);
  $('#TRatio').text(TRatio + "(%)");
  if($('#TRatio').text() == 'NaN(%)'){
    $('#TRatio').text('0(%)');
  }

  var data = {
    labels: [
      "Passed",
      "Running",
      "Failed",
    ],
    datasets: [
      {
        data: [Tpassed, Trunning, Tfailed],
        backgroundColor: [
          "#afe0ad",
          "#88C5FA",
          "#facdd6",
        ],
        hoverBackgroundColor: [
          "#afe0ad",
          "#88C5FA",
          "#facdd6",
        ],
        hoverBorderColor: [
          "#afe0ad",
          "#88C5FA",
          "#facdd6",
        ]
      }]
  };
  var myChart = new Chart(document.getElementById('myChart'), {
    type: 'doughnut',
    data: data,
    options: {
      responsive: true,
      legend: {
        display: false
      },
      cutoutPercentage: 80,
      tooltips: {
        filter: function(item, data) {
          var label = data.labels[item.index];
          if (label) return item;
        }
      }
    }
  });

  textCenter(TRatio, 'myChart');

  function textCenter(val, chartId) {
    Chart.pluginService.register({
      beforeDraw: function(chart) {
        if (chart.canvas.id === chartId) {
        var width = chart.chart.width,
            height = chart.chart.height,
            ctx = chart.chart.ctx;

        ctx.clearRect(0, 0, width, height);

        ctx.restore();
        var fontSize = (height / 114).toFixed(2);
        ctx.font = fontSize + "em sans-serif";
        ctx.textBaseline = "middle";

        var text = val+"%",
            textX = Math.round((width - ctx.measureText(text).width) / 2),
            textY = height / 2;

        ctx.fillText(text, textX, textY);
        ctx.save();
        }
      }
    });
  }
});


