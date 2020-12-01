let pm1;
let pm25;
let pm10;
let power_state;
let fan_speed;

//각각의 경로에 GET요청을 보내 경로에 지정된 함수를 실행
function poweron(){ // 전원 켜기
    $.getJSON('/poweron',
            function(data) {
        }); // /poweron 경로에 GET요청
        return false;
}
function poweroff(){ //전원 끄기
    $.getJSON('/poweroff',
            function(data) {
        }); // /poweroff 경로에 GET요청
        return false;
}
function modeauto(){ // 자동모드
    $.getJSON('/modeauto',
            function(data) {
        }); // /modeauto 경로에 GET요청
        return false;
}

function fanslow(){ // 팬속도 30%
    $.getJSON('/fanslow',
            function(data) {
        }); // /fanslow 경로에 GET요청
        history.back(); //뒤로가기
        return false;
}
function fanmid(){ //팬 속도 65%
    $.getJSON('/fanmid',
            function(data) {
        }); // /fanmid 경로에 GET요청
    history.back(); //뒤로가기
    return false;
}
function fanfull(){ //팬 속도 100%
    $.getJSON('/fanfull',
            function(data) {
        }); // /fanfull 경로에 GET요청
        history.back();//뒤로가기
    return false;
}


let intervalID= setInterval(update_dust, 1000); //1초마다 update_dust() 함수 반복 실행
function update_dust() {
    $.getJSON('/stuff', //ajax로 실시간 미세먼지값 수신
    function (data) {
    console.log(data);
    //변수에 실시간 데이터값 저장(int)
    pm1= Number(data.pm1);
    pm25= Number(data.pm25);
    pm10= Number(data.pm10);
    power_state= Number(data.power_state);
    fan_speed= data.fan_speed;
    // 실시간 미세먼지 값을 해당 id 태그에 업데이트
    $('#dustvalue1').text(pm1);
    $('#dustvalue2').text(pm25);
    $('#dustvalue3').text(pm10);
    
    if (fan_speed=="SLOW"){//팬 속도가 1단계일때
        $('#fan_speed').text("1단계"); //팬 스위치에 상태 표시
    }
    else if(fan_speed == "MID"){//팬 속도가 2단계일때
        $('#fan_speed').text("2단계"); //팬 스위치에 상태 표시
    }
    else if(fan_speed == "FULL"){//팬 속도가 3단계일때
        $('#fan_speed').text("3단계"); //팬 스위치에 상태 표시
    }
    else{
        $('#fan_speed').text("Error");
        console.log("풍량표시 오류")
    }

    //미세먼지 이모티콘 및 색 변화
    if((pm10 <= 30) && ((pm25 + pm1) <= 15)){ //좋음
        $("#duststate").css("color", "#a3e7d6");
        $('#duststate').text("좋음");
        $("#good").css("display", "block"); //좋음 이모티콘만 표시
        $("#normal").css("display", "none"); //나머지 숨김
        $("#bad").css("display", "none"); //나머지 숨김
        $("#verybad").css("display", "none"); //나머지 숨김
        console.log("좋음")
    }else if((pm10 <= 80) && ((pm25 + pm1) <= 35)){ //보통
        $("#duststate").css("color", "#77dd77");
        $('#duststate').text("보통");
        $("#good").css("display", "none"); //나머지 숨김
        $("#normal").css("display", "block"); //보통 이모티콘만 표시
        $("#bad").css("display", "none"); //나머지 숨김
        $("#verybad").css("display", "none"); //나머지 숨김
        console.log("보통")
    }else if((pm10 <= 150) && ((pm25 + pm1) <= 75)){ //나쁨
        $("#duststate").css("color", "#fd9a18");
        $('#duststate').text("나쁨");
        $("#good").css("display", "none"); //나머지 숨김
        $("#normal").css("display", "none"); //나머지 숨김
        $("#bad").css("display", "block"); //나쁨 이모티콘만 표시
        $("#verybad").css("display", "none"); //나머지 숨김

    }else if((pm10 >150) || ((pm25 + pm1) > 75)){ //매우나쁨
        $("#duststate").css("color", "red");
        $('#duststate').text("매우나쁨");
        $("#good").css("display", "none"); //나머지 숨김
        $("#normal").css("display", "none"); //나머지 숨김
        $("#bad").css("display", "none"); //나머지 숨김
        $("#verybad").css("display", "block"); //매우나쁨 이모티콘만 표시
    }else{
        console.log("미세먼지 상태 표시 오류")
        $('#duststate').text("Error!");
    }
    if (power_state == 0){ //전원이 꺼져있을때
        $("#switch1").prop("checked", false); //전원스위치 체크해제(Off)
        $('#switch2').attr("disabled", true); // 자동모드 스위치 비활성화
        $("#sw2lb").css("background-color", "#bebebe"); // 자동모드 스위치 회색으로 설정
    }else{ // 켜져있거나 자동모드일때
        $("#switch1").prop("checked", true); //전원스위치 체크(On)
        $('#switch2').removeAttr("disabled"); // 비활성화 해제
    }

    if (power_state == 2){ // 자동모드일때
        $("#switch2").prop("checked", true); //자동모드 스위치 체크
        $("#sw2lb").css("background-color", "#0bba82"); // 자동모드 스위치 초록색으로
    }else if(power_state ==1){
        $("#switch2").prop("checked", false);//자동모드 스위치 체크해제
        $("#sw2lb").css("background-color", "#ed4956");// 자동모드 스위치 빨간색으로
    }else{ //자동모드가 아닐때
        $("#switch2").prop("checked", false);
        $("#sw2lb").css("background-color", "#bebebe");// 자동모드 스위치 회색으로
    }
    });
    
};

function powerctrl(){ // 파워스위치 누를시 실행, 파워모드 변경
    console.log("파워조정");
    if (power_state == 0){ //전원이 꺼져있을때 누르면
        poweron(); //전원켬
    }
    else if (power_state == 1){ //전원이 켜져있을때 누르면
        poweroff(); //전원끔
    }
    else if (power_state == 2){ //자동모드 일때 누르면
        poweroff(); //전원끔
    }
    else{ //변수 오류 방지
        console.log("전원 변수 오류")
    }
};
function autoctrl(){ // 자동모드 스위치 누를시 실행, 자동모드 설정 및 해제
    console.log("모드조정");
    if (power_state == 1){ //전원이 켜져있을때 누르면
        modeauto(); //자동모드로 설정
    }
    else if (power_state == 2){ //자동모드 일때 누르면
        poweron(); //자동모드 끔(전원켬 상태로 변경)
    }
    else{
        console.log("전원 변수 오류");
    }
};








  // ajax로 전원 끄기(비동기)
  // function poweroff(){
  //     console.log("전원 끔");
  //     alert("전원 끔");
  // }
  // //

//   $(function() {
//     $('a#off').bind('click', function() {
//       $.getJSON('/poweroff',
//           function(data) {
//         //do nothing
//       });
//       return false;
//     });
//   });